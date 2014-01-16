#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-12-01 10:07:08 
# Copyright 2013 NONE rights reserved.
import urllib
import urllib2
from bs4 import BeautifulSoup
import time
import logging
import weibo_login 
import sys
import os
import conf
from wapWeiboFetcher import Fetcher as F
logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s', level=logging.DEBUG)
import re
import urlparse
import random

GF = None
g_proxys = []
g_user_i = 0
g_proxy_i = -1
g_max_switch_time = 10000

def switchConf(u=True, p=True):
    """
    return new proxy and user index
    """
    global g_proxy_i, g_user_i, g_proxys
    proxy=None
    userConf = None
    if len(g_proxys) != 0 and p:
        g_proxy_i = random.randint(0, len(g_proxys)-1)    
        proxy = g_proxys[g_proxy_i]
    if u:
        g_user_i = random.randint(0, len(conf.loginConf)-1)
        userConf = conf.loginConf[g_user_i]
    return userConf, proxy
        
def locateCookieFile(username, cookieStoreBase):
    return cookieStoreBase+'.'+username + '.dev.dat'

def initGF(force=False):
    global GF
    userConf, proxy = switchConf()
    username, passwd = userConf
    cookieFile = locateCookieFile(username, conf.cookieStoreBaseWap)
    if force == True:
        try:
            os.remove(cookieFile)
        except Exception, e:
            pass
    GF = F(username, passwd, cookieFile, False, proxy)
    
    c = 0
    #max_times = g_max_switch_time
    max_times = 2
    aSwitched = False
    while True:
        c += 1
        status = GF.makeSureLoginOK()
        if status == True:
            return True
        if aSwitched:
            GF.switch(proxy, (username, passwd), cookieFile, True)    
            status = GF.makeSureLoginOK()
        if status == True:
            return True
        if status == 'blocked':
            logging.error('[%d] rounds in initGF GF.makeSureLoginOK() returns blocked' % c)
            userConf, proxy = switchConf(u=True, p=True)
        if status == 'timeout':
            logging.error('[%d] rounds in initGF GF.makeSureLoginOK() returns timeout' % c)
            userConf, proxy = switchConf(p=True)
        if c > max_times:   
            logging.error('[%d] rounds in initGF GF.makeSureLoginOK() returns Fale' % c)
            userConf, proxy = switchConf(u=True, p=True)
        time.sleep(60)
        username, passwd = userConf
        cookieFile = locateCookieFile(username, conf.cookieStoreBaseWap)
        if not aSwitched:
            GF.switch(proxy, (username, passwd), cookieFile)
            aSwitched = True
    return False

###### init proxys
def initProxys():
    ret = ['',]
    with open(conf.proxyF) as f:
        ret = f.readlines()
    return [x.strip() for x in ret if x[0]!='#'] 
g_proxys = initProxys()
#g_proxys = ['']
####

#login while importing
if initGF() != True:
    logging.error('login weibo failed, exit')
    sys.exit(-1)
else:
    logging.info("GF initialed")


def getUserUrl(user):
    return 'http://weibo.com/' + user 

def getWapUserUrl(user):
    return 'http://weibo.cn/' + user 

def combineUrl(base, url):
    return urlparse.urljoin(base, url)

def requestPage(url):
    "with auto switch"
    global GF, g_max_switch_time
    response = None
    c = 0
    aSwitched = False
    while c <= g_max_switch_time:
        c += 1
        try:
            response = GF.safeFetch(url)
            reUrl = response.geturl().strip()
            page = response.read()
            try: 
                page = page.decode('utf-8')
            except Exception, e:
                logging.debug('fail in decode by utf-8 [e:%s][url:%s], try GBK' % (e, url))
                page = page.decode('GBK')
            response.close()
            if page != None and page != '':
                return page, url
        except Exception, e:
            if response == None:
                logging.debug('round[%d] fail in request [%s][%s], will sleep and switch' % (c, e, url))
                time.sleep(30)
                #switch
                userConf, proxy = switchConf()
                username, passwd = userConf
                cookieFile = locateCookieFile(username, conf.cookieStoreBaseWap)
                logging.debug('[e:%s][%s] switch into [%s:%s]' % (e, url, userConf, proxy))
                if not aSwitched:
                    GF.switch(proxy, (username, passwd), cookieFile)
                    aSwitched = True
                else:
                    GF.switch(proxy, (username, passwd), cookieFile, True)    
            else:      
                logging.error("unknown in request: [e:%s][url:%s][userConf:%s][proxy:%s][respone:%s]" \
                % (e, url, userConf, proxy, respone))
                continue
    return '', ''

def getUserFollowerInfo(page):
    re_weibo = re.compile(ur'<span.+>微博\[(\d+)\]</span>.*'\
                            ur'<a href="(.+)">关注\[(\d+)\]</a>.*'\
                            ur'<a href="(.+)">粉丝\[(\d+)\]</a>')
    soup = BeautifulSoup(page) 
    #print soup.prettify().encode('utf-8')
    ret = soup.body.find_all(name='div', attrs={'class':'tip2'})
    for each in ret:
        data = unicode(each)
        got = re_weibo.search(data)
        if got != None:
            got = got.groups()
            flwerUrl = got[3]
            nFlwer = int(got[4])
            flweeUrl = got[1]
            nFlwee = int(got[2])
            return flwerUrl, nFlwer, flweeUrl, nFlwee
    return None, None, None, None

def pickUserId(url):
    ret = urlparse.urlsplit(url)
    return str(ret.path)

def pickBaseUrl(url):
    ret = urlparse.urlsplit(url)
    return str(ret.scheme+'://'+ret.netloc)

def extractUsers(page):
    re_user = re.compile(ur'<a href="(.+)">(.+)</a>.*?<br/>粉丝\d+人<br/>')
    soup = BeautifulSoup(page)
    ret = soup.body.find_all(name='td', attrs={'valign':'top'})
    userList = []
    href = ''
    for each in ret:
        each = unicode(each)
        got = re_user.search(each)
        if got != None:
            got = got.groups()
            uId = pickUserId(got[0])
            uName = got[1]
            userList.append((uId, uName))
    ret = soup.body.find(name='a', text=u'下页') 
    if ret != None:
        href = ret.get('href')
    return userList, href

def findFollowers(flwerUrl):
    nextUrl = flwerUrl
    retUser = []
    while True:
        #print nextUrl
        page, reUrl = requestPage(nextUrl)
        if page == '':
            loggng.error("holy continue")
            continue
        flwList, nextUrl = extractUsers(page)
        #print len(flwList)
        retUser += flwList
        if nextUrl == '':
            break
        nextUrl = combineUrl(reUrl, nextUrl)
    return retUser

def findFollowees(flweeUrl):
    nextUrl = flweeUrl
    retUser = []
    while True:
        #print nextUrl
        page, reUrl = requestPage(nextUrl)
        if page == '':
            loggng.error("holy continue")
            continue
        flwList, nextUrl = extractUsers(page)
        #print len(flwList)
        retUser += flwList
        if nextUrl == '':
            break
        nextUrl = combineUrl(reUrl, nextUrl)
    return retUser

def gotBilateral(userFlwers, userFlwees):
    return list(set(userFlwers) & set(userFlwees))

def getUserFollower(user):
    userUrl = getWapUserUrl(user)
    data, reUrl = requestPage(userUrl)
    #do ana
    flwerUrl, nFlwer, flweeUrl, nFlwee = getUserFollowerInfo(data)
    flwerUrl = combineUrl(reUrl, flwerUrl)
    flweeUrl = combineUrl(reUrl, flweeUrl)
    #print flwerUrl, nFlwer, flweeUrl, nFlwee
    userFlwers = findFollowers(flwerUrl)
    userFlwees = findFollowees(flweeUrl)
    #print len(userFlwers), len(userFlwees)
    bis = gotBilateral(userFlwers, userFlwees) 
    logging.info('get getUserFollower(%s) flwr(%d), flwee(%d) bi(%d)'%(user, len(userFlwers), len(userFlwees), len(bis)))
    return userFlwers, userFlwees, bis

def findUserInfoUrl(page):
    re_weibo = re.compile(ur'<a href="([^ ]+?)">资料</a>')
    got = re_weibo.search(page)
    if got != None:
        got = got.groups()
        infoUrl = got[0]
        return infoUrl
    logging.error("no userInfo url in page:[%s]" % page.replace("\n", ""))
    return None

def pickBasicInfo(text):
    li = text.split("\n")
    ret = {}
    reEmpty = re.compile(ur'\s+| ')
    for l in li:
        #print l
        k = None; v = None
        if ':' in l:
            k, v = l.split(':', 1)
        elif u'：' in l: 
            k, v = l.split(u'：', 1)
        #print k, v
        if k!=None and v!=None:
            v = v.strip()
            v = reEmpty.split(v)
            ret[k] = v
    return ret    

def pickOther(text):
    li = text.split("\n")
    ret = []
    reEmpty = re.compile(ur'\s+| ')
    for l in li:
        l = l.strip()
        if l == '':
            continue
        l = reEmpty.split(l)
        l[0] = l[0].strip(u'·')
        ret.append(l)
    return ret    

def findMoreTag(tagUrl):
    tagList = [] 
    page, reUrl = requestPage(tagUrl)
    soup = BeautifulSoup(page)
    ret = soup.body.find_all(name='div', attrs={'class':['c']})
    beginTag=False
    for div in ret:
        if u'>>标签' in div.text:
            beginTag = True
            continue
        if beginTag == True:
            #print lastF
            for a in div.find_all(name='a'):
                tagList.append(a.text)
            break
    return tagList
    

def findUserInfo(infoUrl):
    retDict = {}
    page, reUrl = requestPage(infoUrl)
    soup = BeautifulSoup(page)
    ret = soup.body.find_all(name='div', attrs={'class':['c', 'tip']})

    beginTag=False
    lastF = ''
    for div in ret:
        if div['class'][0] == 'tip':
            lastF = unicode(div.text)
            if lastF == u'基本信息':
                beginTag = True
            elif lastF == u'其他信息':
                break
    
        if beginTag == True and div['class'][0]=='c':
            #print lastF
            li = str(div).replace('<br/>', "\n")
            div = BeautifulSoup(li)
            if lastF == u'基本信息': 
                retDict = pickBasicInfo(unicode(div.text))
                if u'标签' in retDict and u'更多>>' in retDict[u'标签']:
                    href = div.find(name='a', text=u'更多>>')['href']
                    href = combineUrl(reUrl, href)
                    retDict[u'标签'] = findMoreTag(href)
            else: 
                retLi = pickOther(unicode(div.text))
                retDict[lastF] = retLi
    return retDict

def getUserInfo(user):
    userUrl = getWapUserUrl(user)
    data, reUrl = requestPage(userUrl)
    infoUrl = findUserInfoUrl(data)
    if infoUrl == None:
        return {}
    infoUrl = combineUrl(reUrl, infoUrl)
    userInfo = findUserInfo(infoUrl)
    return userInfo

def getUserContent(user, pages=10):
    userUrl = getWapUserUrl(user)
    nextUrl = userUrl
    retWeibo = []
    c = 0
    while c < pages:
        c += 1
        data, reUrl = requestPage(nextUrl)
        weiboList, nextUrl = extractWeibo(data)
        if nextUrl == None:
            break
        nextUrl = combineUrl(reUrl, nextUrl)
        retWeibo += weiboList
    return retWeibo

def extractWeibo(page):
    soup = BeautifulSoup(page)    
    ret= soup.body.find_all(name='div', id=re.compile(r".+"))
    retList = []
    nextUrl = None
    beginTag=False
    for div in ret:
        #print div
        span = div.find_all(name='span', class_=['ctt', 'cmt'])
        if span != []:
            isRetweet = False
            content = u''
            ddiv = None
            for s in span:
                if s['class'] == ['ctt']: 
                    content += s.text
                elif s['class'] == ['cmt'] and s.text == u'转发理由:':
                    isRetweet = True
                    ddiv = s.find_parent('div')
            if ddiv != None:
                for a in ddiv.find_all(['a','span']):
                    a.extract()
                content = ddiv.text + '//' + content
            retList.append(content)
        else:
            try:
                nextUrl = div.find(name='a', text=u'下页')['href']   
            except TypeError, e:
                logging.debug("no next page [%s] data[%s]" % (e, div)) 
            break
    return retList, nextUrl

def psList(a):
    retString = '['
    ret = []
    for each in a:
        if type(each) == list:
            ret.append(psList(each))
        else:   
            ret.append(each)
    retString += ",".join(ret)
    retString += ']'
    return retString



if __name__ == '__main__':
    #ret = requestPage('http://weibo.cn/cheungzee')
    #print ret[0]
    #ret = getUserInfo('/cheungzee')
    #for each in ret:
    #    print each, psList(ret[each])
    ret = getUserContent('/cheungzee', 2)
    for each in ret:
        print '='*30
        print each


