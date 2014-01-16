#!/usr/bin/python

import sqlite2cookie
import sys
import re
import urllib
import urllib2
import socket
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
import dbOperP
import time
import random
from multiprocessing import Event,Process
import signal
import conf

SUBPROCESSES = []
WORKERS = []
EXIT = Event()

class WeiBoBug:
    def __init__(self):
        # data should be post with request
        self.data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'wsse',
            'sp': '',
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        self.postdata = urllib.urlencode(self.data)
        # change the User-Agent and pretend a browser
        #set user_agent
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0'
        self.headers = {'User-Agent' : self.user_agent }
        fo = open(r"proxy.txt","r")
        self.proxys = fo.read().strip().split("\n")
        fo.close()
        self.be_exit = Event()
        self.be_exit.clear()

    def stop_main_loop(self):
        print "stop_main_loop invoked"
        self.be_exit.set()
        exit()

    def createOpener(self):
        #%APPDATA%\Mozilla\Firefox\Profiles\  火狐浏览器cookie位置 在运行里输入前面的地址即可跳转
        cookiejar = sqlite2cookie.sqlite2cookie(conf.cookiesPath)
        cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
        proxyAdd = self.proxys[random.randint(0,len(self.proxys)-1)]
        print proxyAdd
        proxy_handler = urllib2.ProxyHandler({"http":proxyAdd})
        opener = urllib2.build_opener(cookie_support, proxy_handler, urllib2.HTTPHandler)
        urllib2.install_opener(opener)

    def wapLogIn(self):
        try:
            urlRequest = urllib2.Request('http://weibo.cn/',self.postdata,self.headers)
            response = urllib2.urlopen(urlRequest,timeout=10)
            unicodeLogPage = response.read().decode('utf-8')
            #print unicodeLogPage
            response.close()
        except urllib2.URLError, e:
            if isinstance(e.reason, socket.timeout):
                print "Timeout error: %r" % e
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            self.createOpener()
            self.wapLogIn()
            pass
        except Exception , e:
            print e, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            self.createOpener()
            self.wapLogIn()

    def getSearchList(self):#得到搜索内容list 你需要根据需要自己重写此方法
        dbo = dbOperP.dbOperator()
        results = dbo.selectData("select name,pid from peopleinfor")
        dbo.closeDb()
        return results
    
    def weiBoWapSearchByList(self,lists):#传入需要search的字符串list
        for searchStr in lists:#在这个代码中 每一个元素含有（name，pid）可以改成你需要的格式
            name = searchStr[0].encode("utf-8")
            if name.find("(") > -1:
                name = name[0:name.find("(")]
            pid = searchStr[1]
            print name,pid,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            re = False
            while(re == False):
                re = self.weiBoWapSearch(name,pid)

    def weiBoWapSearch(self,searchStr,pid):#开始搜索 name。pid是为了存入数据库，你可以根据自己的需要改写。searchStr为要搜索的字符串
        url = "http://weibo.cn/search/?vt=4&gsid=4uuxc2441eFZJ7NRKaVggg7vrcu"
        values = {'keyword' : searchStr,'smblog' : '搜微博'}
        data = urllib.urlencode(values) # encoding
        req = urllib2.Request(url,data,self.headers)  # submit data
        try:
            response = urllib2.urlopen(req,timeout=10)  #get response
            unicodePage = response.read().decode('utf-8')  #feedback content
            if response.geturl().strip() == "http://weibo.cn/pub/":
                print "change ip"
                time.sleep(60)
                self.createOpener()
                self.wapLogIn()
                return False
            response.close()
            if self.extractTopic(searchStr,pid,unicodePage,True) == False:
                return True
            if unicodePage.encode('utf-8').find("请尝试更换关键词")>=0:
                print "no result"
                return True
            soup = BeautifulSoup(unicodePage)
            pagelist = soup.find("div",{"id":"pagelist"})
            if pagelist == None:
                if unicodePage.encode('utf-8').find("输入的网址不正确")>=0:
                    print "wrong url"
                    self.createOpener()
                    self.wapLogIn()
                    return False
                return True
            nextLink = pagelist.find("a")
            if nextLink != None:
                nextPageLink = "http://weibo.cn" + nextLink["href"]
                nextPage = True
                cP = 2
                totalPage = 0
                while(nextPage):
                    nextPage = False
                    try:
                        req = urllib2.Request(nextPageLink,self.postdata,self.headers)
                        response = urllib2.urlopen(req,timeout=10)  #get response
                        unicodePage = response.read().decode('utf-8')  #feedback content
                        response.close()
                        if response.geturl().strip() == "http://weibo.cn/pub/":
                            print "change ip"
                            time.sleep(60)
                            self.createOpener()
                            self.wapLogIn()
                            continue
                        if self.extractTopic(searchStr,pid,unicodePage,False) == False:
                            return True
                        if cP == 2:
                            soup = BeautifulSoup(unicodePage)
                            pagelist = soup.find("div",{"id":"pagelist"})
                            if pagelist == None:
                                if unicodePage.encode('utf-8').find("输入的网址不正确")>=0:
                                    print "wrong url"
                                    self.createOpener()
                                    self.wapLogIn()
                                    return False
                                return True
                            nextLink = pagelist.find("a")
                            nextPageLink = "http://weibo.cn" + nextLink["href"]
                            totalPage = int(pagelist.find("input",{"name":"mp"})['value'])
                            print totalPage
                            nextPage = True
                            cP +=1
                        elif cP <= totalPage:
                            cP +=1
                            pagel = nextPageLink.split("page=")
                            nextPageLink = "%spage=%i&st=%s" % (pagel[0],cP,nextPageLink.split("&st=")[-1])
                            nextPage = True
                    except urllib2.URLError, e:
                        if isinstance(e.reason, socket.timeout):
                            print "Timeout error: %r" % e
                        if hasattr(e, 'reason'):
                            print 'We failed to reach a server.'
                            print 'Reason: ', e.reason, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                        elif hasattr(e, 'code'):
                            print 'The server couldn\'t fulfill the request.'
                            print 'Error code: ', e.code, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                        self.createOpener()
                        self.wapLogIn()
                        nextPage = True
                        pass

                    except Exception , e:
                        nextPage = True
                        print e, searchStr,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                        self.createOpener()
                        self.wapLogIn()
                        pass

        except urllib2.URLError, e:
            if isinstance(e.reason, socket.timeout):
                print "Timeout error: %r" % e
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            self.createOpener()
            self.wapLogIn()
            pass
        except Exception , e:
            print e, searchStr,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            self.createOpener()
            self.wapLogIn()
            return False

        return True

    def getretweet(self,url,idstr):#得到转发的微博
        dbo = dbOper.dbOperator()
        req = urllib2.Request(url,None,self.headers)
        response = urllib2.urlopen(req,timeout=5)  #get response
        unicodePage = response.read().decode('utf-8')  #feedback contents
        response.close()
        soup = BeautifulSoup(unicodePage)        
        items = soup.findAll("div",{"class":"c"})
        i=0
        for item in items:          
            if item.find("span",{"class":"ct"})<0:
                continue          
            i+=1
            if i == 1:
               continue
            str1 = item.renderContents()
            text1 = str1.split('">')[1]
            userstr = text1.split('<')[0]
            textstr=''
            for t2 in item.findAll(True):
                t2.hidden = True
            text2 = item.renderContents()
            textstr = text2.strip().split("&nbsp;")[0].split(userstr+':')[1]

            '''get time begin'''
        
            subs = item.findAll("span",{"class":"ct"})
            for t in subs[0].findAll(True):
                t.hidden = True
            substr = subs[0].renderContents()
            substr = substr.strip().split("&nbsp;")[0]
            timeStr = ''
            if substr.find('分钟前') > -1:
                timeStr = time.strftime("%Y-%m-%d %H:%M:00",time.localtime(time.time()))
            elif substr.find('今天') > -1:
                timeStr = time.strftime("%Y-%m-%d ",time.localtime(time.time())) + substr.split(" ")[1]
            elif substr.find('月') > -1:
                dateStr = filter(str.isdigit, substr.split(" ")[0])
                timeStr = time.strftime("%Y-",time.localtime(time.time())) + dateStr[0:2] + "-" + dateStr[2:] + " " + substr.split(" ")[1] + ":00"
            else:
                timeStr = substr
            #print 'time:',timeStr
            '''get time end''' 
                
            #value = [None,wbid,username,content,date]    
            value = [None,idstr,userstr,textstr,timeStr]
            dbo.insertRetweet(value)
        dbo.closeDb()

        pagelist = soup.find("div",{"id":"pagelist"})
        if pagelist == None:
            return False        
        elif pagelist.renderContents().find("下页")>0:
            return True
        else:
            return False

    def extractTopic(self,searchStr,pid,unicodePage,firstPage):#抓取每一条微博
        soup = BeautifulSoup(unicodePage)
        items = soup.findAll("div",{"class":"c"})
        dbo = dbOperP.dbOperator()

        total = 0

        removeFirst = False

        for item in items:
            idstr = item.get("id",None)
            if idstr:#weibo id 'M_AeJs808NB'
                if firstPage and removeFirst == False:
                    removeFirst = True
                    continue
                seleResult = dbo.selectData("select pid from data where wbid = \'%s\'" % idstr)
                if len(seleResult) > 0:
                    opid = seleResult[0][0]
                    if opid == pid:
                        total += 1
                        continue
                    else:
                        total = 0
                    if total >= 3:
                        dbo.closeDb()
                        return False

                '''item weibo text div'''

                #get retweet
                contentStr1 = item.renderContents()
                i=contentStr1.find(r'>转发[')    
                if i>0:
                    retweetNum = int(contentStr1[i+8])
                    if retweetNum>0:
                        hr=contentStr1[:i].split("&nbsp;")[-1]
                        rturl=hr.split(r'"')[1]

                        if rturl.find('cmt')<0:
                            rturl=rturl.replace('amp;','')
                            page=1
                            go = True
                            while (go):
                                url=rturl+'&page='+str(page)
                                go = self.getretweet(url,idstr)
                                page+=1

                '''get time begin'''
                subs = item.findAll("span",{"class":"ct"})
                for t in subs[0].findAll(True):
                    t.hidden = True
                substr = subs[0].renderContents()
                substr = substr.strip().split("&nbsp;")[0]
                timeStr = ''
                if substr.find('分钟前') > -1:
                    timeStr = time.strftime("%Y-%m-%d %H:%M:00",time.localtime(time.time()))
                elif substr.find('今天') > -1:
                    timeStr = time.strftime("%Y-%m-%d ",time.localtime(time.time())) + substr.split(" ")[1]
                elif substr.find('月') > -1:
                    dateStr = filter(str.isdigit, substr.split(" ")[0])
                    timeStr = time.strftime("%Y-",time.localtime(time.time())) + dateStr[0:2] + "-" + dateStr[2:] + " " + substr.split(" ")[1] + ":00"
                else:
                    timeStr = substr
                '''get time end'''
                for sub in subs:
                    sub.extract()
                for tag in item.findAll(True):
                    tag.hidden = True
                contentStr = item.renderContents()
                if contentStr.find("转发了") >= 0:
                    continue
                contentStr = contentStr.replace("&nbsp;","")
                contentStr = contentStr.replace("<!-- -->","")
                result, number = re.subn('赞.*收藏', "", contentStr)
                del number
                splitIndex = result.find(':')
                userName = result[0:splitIndex]
                content = result[splitIndex+1:]
                value = [None,pid,idstr,userName,content,timeStr]
                try:
                    dbo.insert(value)
                except:
                    pass
        dbo.closeDb()
        return True

    def run(self,lists):
        self.createOpener()
        self.wapLogIn()
        self.weiBoWapSearchByList(lists)


#other function ---------------------------------------------------------------
'''多进程 ctrl+c 杀死所有进程
for i in range(9):
    w = WeiBoBug()
    WORKERS.append(w)
def wrap(worker,lists):
    worker.run(lists)

def exit_handler(signum, frame):
    print "signal handler called with signal ", signum, " ", WORKERS, " ", frame
    EXIT.set()
    time.sleep(1)
    print "------------------------------workers",len(WORKERS)
    for w in WORKERS:
        print "begin to invoke stop_main_loop"
        w.stop_main_loop()

signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)
'''

if __name__ == '__main__':
    print "-------------------------------------------------------------"
    print "begin", time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    print sqlite2cookie.sqlite2cookie(conf.cookiesPath)
    sys.exit(1)
    bug = WeiBoBug()
    res = bug.getSearchList()

    #单进程执行
    bug.createOpener()
    bug.wapLogIn()
    bug.weiBoWapSearchByList(res)

    #多进程
    '''
    p1 = Process(target=wrap, args=(WORKERS[0],res[0:20000],))
    p1.daemon=True
    p2 = Process(target=wrap, args=(WORKERS[1], res[20000:40000],))
    p2.daemon=True
    p3 = Process(target=wrap, args=(WORKERS[2], res[40000:60000],))
    p3.daemon=True
    p4 = Process(target=wrap, args=(WORKERS[3], res[60000:],))
    p4.daemon=True
    p5 = Process(target=wrap, args=(WORKERS[4], res[40000:50000],))
    p5.daemon=True
    p6 = Process(target=wrap, args=(WORKERS[5], res[50000:60000],))
    p6.daemon=True
    p7 = Process(target=wrap, args=(WORKERS[6], res[60000:70000],))
    p7.daemon=True
    p8 = Process(target=wrap, args=(WORKERS[7], res[70000:80000],))
    p8.daemon=True
    p9 = Process(target=wrap, args=(WORKERS[8], res[80000:],))
    p9.daemon=True
    
    #print len(WORKERS),"***************************"

    SUBPROCESSES.append(p1)
    SUBPROCESSES.append(p2)
    SUBPROCESSES.append(p3)
    SUBPROCESSES.append(p4)
    SUBPROCESSES.append(p5)
    SUBPROCESSES.append(p6)
    SUBPROCESSES.append(p7)
    SUBPROCESSES.append(p8)
    SUBPROCESSES.append(p9)

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    p9.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()
    p9.join()
    '''
    print "finished", time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
