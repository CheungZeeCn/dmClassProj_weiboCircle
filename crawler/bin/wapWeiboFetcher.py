#!/usr/bin/env python
# -*- coding: utf-8 -*-  
import urllib2
import urllib
import cookielib
import traceback
import socket
import logging
formatStr = ('%(asctime)s [%(levelname)s][%(filename)s:%(lineno)s]:'
                     ' %(message)s')
logging.basicConfig(format=formatStr, level=logging.DEBUG)
import time
import os
import lxml.html as HTML
import urlparse


class Fetcher(object):
    def __init__(self, username=None, pwd=None, cookie_filename=None, force=False, proxyName=None):
        """if force is True, do login"""
        self.loaded = False
        self.proxyName = proxyName
        self.cookie_filename = cookie_filename
        self.openerOK = self.installOpener(cookie_filename, self.proxyName)
        self.username = username
        self.pwd = pwd
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}
        if force == True or self.loaded == False:
            self.login()   
    
    def installOpener(self, cookie_filename, proxyName):
        # cookie
        logging.info("installOpener cookie_filename[%s], proxyName[%s]" % (cookie_filename, proxyName))
        cj = None
        loaded = False
        opener = None
        proxy = None
        cookie_processor = None

        if (cookie_filename != None and cookie_filename != '') and os.path.exists(cookie_filename):
            try:
                cookie_jar  = cookielib.LWPCookieJar(cookie_filename)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                cj = cookie_jar
                loaded = True
                logging.info('Loading cookies done')
            except cookielib.LoadError:
                cj = cookielib.LWPCookieJar()
                loaded = False
                logging.error('Loading cookies error')
        else: #clean cookie
            logging.info("clean the cookies: cookie_filename[%s]" % (cookie_filename))
            cj = cookielib.LWPCookieJar()
            loaded = False
        cookie_processor = urllib2.HTTPCookieProcessor(cj)
        try:
            if proxyName != None and proxyName != '':
                proxy = urllib2.ProxyHandler({'http':proxyName})
                opener = urllib2.build_opener(cookie_processor, proxy, urllib2.HTTPHandler)
            else:
                opener = urllib2.build_opener(cookie_processor, urllib2.HTTPHandler)
        except Exception, e:
            logging.error("build opener failed[%s][cookie_filename:%s][proxyName:%s]" % (e, cookie_filename, proxyName))

        if opener != None:
            self.cj = cj
            if (cookie_filename != None and cookie_filename != ''):
                self.cookie_filename = cookie_filename
            self.opener = opener
            if proxyName != None and proxyName != '':
                self.proxyName = proxyName
                self.proxy = proxy
            logging.debug("installOpener OK cookie_filename[%s], proxyName[%s]" % (cookie_filename, proxyName))
            return True  
        return False

    def switch(self, proxyName=None, user=None, cookie_filename=None, relogin=False):
        """ """
        logging.debug("switch[proxyName=%s, user=%s, cookie_filename=%s, relogin=%s]" \
                        % (proxyName, user, cookie_filename, relogin))
        if user != None:
            self.username, self.pwd = user  
        if relogin == True:
            cookie_filename = None
        logging.debug("before install in switch")
        self.openerOK = self.installOpener(cookie_filename, self.proxyName) 
        if self.openerOK == False:
            return False
        if relogin == True:
            return self.login()
        return True
    
    def get_rand(self, url):
        headers = {'User-Agent':'Mozilla/5.0 (Windows;U;Windows NT 5.1;zh-CN;rv:1.9.2.9)Gecko/20100824 Firefox/3.6.9',
                   'Referer':''}
        req = urllib2.Request(url ,urllib.urlencode({}), headers)
        page, status, reUrl = self.openRequest(req)
        if page == None:
            return '', '', '' 
        login_page = page
        ok = False
        try:
            rand = HTML.fromstring(login_page).xpath("//form/@action")[0]
            passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
            vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
            ok = True
        except lxml.etree.XMLSyntaxError, e:
            logging.error("%s" % e)
        if ok == False:
            return '', '', '' 
        return rand, passwd, vk
    
    def login(self, username=None, pwd=None, cookie_filename=None):
        """do login and store cookies in cookie_filename"""
        logging.debug('doing the login action')
        if self.username is None or self.pwd is None:
            self.username = username
            self.pwd = pwd
        if cookie_filename == None:
            cookie_filename = self.cookie_filename 
        assert self.username is not None and self.pwd is not None
        #re install opener
        #self.installOpener('', '')
        
        url = 'http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='
        rand, passwd, vk = self.get_rand(url)
        if rand == '':
            logging.error('get rand failed')
            return False

        data = urllib.urlencode({'mobile': self.username,
                                 passwd: self.pwd,
                                 'remember': 'on',
                                 'backURL': 'http://weibo.cn/',
                                 'backTitle': '新浪微博',
                                 'vk': vk,
                                 'submit': '登录',
                                 'encoding': 'utf-8'})
        url = 'http://3g.sina.com.cn/prog/wapsite/sso/' + rand
        req = urllib2.Request(url, data, self.headers)
        page, status, reUrl = self.openRequest(req)
        #print "\n", page, "\n"
        if page == None or page == '': # login failed
            logging.error('login failed')
            return False 
        link = HTML.fromstring(page).xpath("//a/@href")[0]
        if not link.startswith('http://'): 
            link = 'http://weibo.cn/%s' % link
        req = urllib2.Request(link, headers=self.headers)
        page, status, reUrl = self.openRequest(req)
        logging.debug("link:[%s] reUrl[%s]" % (link,reUrl))
        #print "\n", page, "\n"
        if 'http://weibo.cn/pub/' == reUrl:
            logging.error('login failed, blocked')
            return  False
        if cookie_filename is not None:
            logging.debug("saving cookies in file")
            self.cj.save(filename=cookie_filename)
        elif self.cj.filename is not None:
            self.cj.save()
        logging.info('login success!')
        return True

    def openRequest(self, req):
        try:
            url =  req.get_full_url()
            resp = self.opener.open(req)
            reUrl = resp.geturl()
            page = resp.read()
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                logging.error('Reason: [%s] [%s]' % (e.reason, url))
                return (None, 'timeout', '')
            elif hasattr(e, 'code'):
                logging.error('Error code: [%s] [%s]' % (e.code, url))
                return (None, 'timeout', '')
            logging.error('failed [%s] in open[%s]' % (e, url))    
        except Exception, e:
            logging.error('failed [%s] in open[%s]' % (e, url))    
            return (None, 'blocked', '')
        return (page, 'ok', reUrl)
        
    def fetch(self, url, timeout=60):
        try:
            req = urllib2.Request(url, headers=self.headers)
            resp = self.opener.open(req)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                logging.error('Reason: [%s] [%s]' % (e.reason, url))
                return (None, 'timeout')
            elif hasattr(e, 'code'):
                logging.error('Error code: [%s] [%s]' % (e.code, url))
                return (None, 'timeout')
            logging.error('failed [%s] in open[%s]' % (e, url))    
        except Exception, e:
            #exstr = traceback.format_exc() 
            #logging.error('error[%s], url[%s] trace[%s]' % (e, url, exstr))
            logging.error('error[%s], url[%s] trace[%s]' % (e, url, 'not open'))
            return (None, 'timeout')
        return (resp, 'ok')

    def makeSureLoginOK(self, timeout=20):
        url = 'http://weibo.cn/cheungzee'
        resp, status = self.fetch(url) 
        if resp == None:
            return False   
        reUrl = resp.geturl().strip()
        times = 0
        firstTime = time.time()
        while not self.theSameUrl(reUrl, url):
            times += 1
            logging.error('error in  makeSureLoginOK\'sfetch[[%s][%s]][times:%d], will relogin' % (url, reUrl, times))
            logging.debug("debug: self.cookie_filename[%s], self.proxyName[%s]"%(self.cookie_filename, self.proxyName))
            if self.login() == False: 
                return False  
            resp, status = self.fetch(url) 
            if resp == None:
                return False
            reUrl = resp.geturl().strip()
            if reUrl == 'http://weibo.cn/pub/': #blocked
                return 'blocked'
            if not self.theSameUrl(reUrl, url):
                logging.error('error in makeSureLoginOK[[url:%s][reUrl:%s] and re login, sleep 10s' % (url, reUrl))
                #logging.error('error in makeSureLoginOK[[%s] and re login, sleep 60s, data:%s' % (url, resp.read()))
                time.sleep(10)
            if time.time() - firstTime >= timeout:
                logging.error('error in makeSureLoginOK for timepass[%f]-[%f] logintimes[%d] and timeout[%d], failed' % (time.time(), firstTime,  times, timeout))
                logging.error('dump page blocked data[%s]' % (resp.read().replace("\n", '')))
                return 'blocked'
        return True
    
    def safeFetch(self, url):
        resp, status = self.fetch(url) 
        if resp == None:
            return None
        reUrl = resp.geturl().strip()
        if not self.theSameUrl(reUrl, url):
            logging.error('error in safeFetch[[%s][%s] and re login, call makeSureLoginOK' % (url, reUrl))
            loginStatus = self.makeSureLoginOK()
            if loginStatus == False:
                return None
            elif status == 'blocked':
                return 'blocked'
            else:
                resp, status = self.fetch(url) 
                if resp == None:
                    return 'timeout'
        return resp

    def theSameUrl(self, url1, url2):
        u1 = urlparse.urlsplit(url1)
        u2 = urlparse.urlsplit(url2)
        if u1.scheme+u1.netloc+u1.path ==\
            u2.scheme+u2.netloc+u2.path:
            return True
        return False

if __name__ == '__main__':
    #f= Fetcher('weibocir@126.com', 'weiboCirCir', 'test_ck_jar_3', proxyName="http://115.25.216.6:80")   
    f= Fetcher('weibocir1@126.com', 'weiboCirCir', 'test_ck_jar_weibocir@126.com')   
    #username=None, pwd=None, cookie_filename=None, force=False, proxyName=None
    print "fetch return", f.safeFetch('http://weibo.cn/cheungzee')
    print "\n" * 4
    print "switch proxy"
    print f.switch('http://202.116.160.89:80', ('weibocir1@126.com', 'weiboCirCir' ),  cookie_filename="test_ck_jar_1")
    print "fetch return", f.safeFetch('http://weibo.cn/cheungzee')
    print "\n" * 4
    print f.switch('http://115.25.216.6:80', cookie_filename="test_ck_jar")
    print "fetch return", f.safeFetch('http://weibo.cn/cheungzee')
    

        #print f.switch(proxy='http://114.141.162.53:8080')
    
