#!/usr/bin/env python
#coding=utf8

'''
Created on Mar 18, 2013

@author: yoyzhou
'''
import logging

try:
    import os
    import sys
    import urllib
    import urllib2
    import cookielib
    import base64
    import re
    import hashlib
    import json
    import rsa
    import binascii
    import lxml.html as HTML

except ImportError:
        print >> sys.stderr, """\

There was a problem importing one of the Python modules required.
The error leading to this problem was:

%s

Please install a package which provides this module, or
verify that the module is installed correctly.

It's possible that the above module doesn't match the current version of Python,
which is:

%s

""" % (sys.exc_info(), sys.version)
        sys.exit(1)


__prog__= "weibo_login"
__site__= "http://yoyzhou.github.com"
__weibo__= "@pigdata"
__version__="0.1 beta"


def get_prelogin_status(url):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0', 'Referer':''}
    req = urllib2.Request(url ,urllib.urlencode({}), headers)
    resp = urllib2.urlopen(req)
    login_page = resp.read()
    rand = HTML.fromstring(login_page).xpath("//form/@action")[0]
    passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
    vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
    return rand, passwd, vk


def login(username, pwd, cookie_file, force=False):
    """"
        Login with use name, password and cookies.
        (1) If cookie file exists then try to load cookies;
        (2) If no cookies found then do login
    """
    #If cookie file exists then try to load cookies
    if os.path.exists(cookie_file) and force == False:
        try:
            cookie_jar  = cookielib.LWPCookieJar(cookie_file)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
            loaded = 1
        except cookielib.LoadError:
            loaded = 0
            logging.error('Loading cookies error')
        
        #install loaded cookies for urllib2
        if loaded:
            cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
            opener         = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
            urllib2.install_opener(opener)
            logging.info('Loading cookies success')
            return 1
        else:
            return do_login(username, pwd, cookie_file)
    
    else:   #If no cookies found
        print "do_login"
        return do_login(username, pwd, cookie_file)


def do_login(username,pwd,cookie_file):
    """"
    Perform login action with use name, password and saving cookies.
    @param username: login user name
    @param pwd: login password
    @param cookie_file: file name where to save cookies when login succeeded 
    """
    cookie_jar2     = cookielib.LWPCookieJar()
    cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
    opener2         = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
    urllib2.install_opener(opener2)
    pre_login_url = 'http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='
    try:
        rand, passwd, vk = get_prelogin_status(pre_login_url)
    except:
        return False

    login_data = {
                    'mobile': username,
                    passwd: pwd,
                    'remember': 'on',
                    'backURL': 'http://weibo.cn/',
                    'backTitle': '新浪微博',
                    'vk': vk,
                    'submit': '登录',
                    'encoding': 'utf-8',}
    
    #Fill POST data
    login_data = urllib.urlencode(login_data)
    http_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    login_url = 'http://3g.sina.com.cn/prog/wapsite/sso/' + rand
    req_login  = urllib2.Request(
        url = login_url,
        data = login_data,
        headers = http_headers
    )
    try:
        result = urllib2.urlopen(req_login)
        page = result.read()
    except Exception, e:
        logging.error('error[%s], req_login[%s]' % (e, req_login))
        return False
    link = HTML.fromstring(page).xpath("//a/@href")[0]
    if not link.startswith('http://'): 
        link = 'http://weibo.cn/%s' % link
    req = urllib2.Request(link, headers=http_headers)
    try:
        urllib2.urlopen(req)
        cookie_jar2.save(cookie_file,ignore_discard=True, ignore_expires=True)
    except Exception, e:
        logging.error('error[%s], req[%s]' % (e, req))
        return False

    req = urllib2.Request('http://weibo.cn/cheungzee', headers=http_headers) 
    return True


if __name__ == '__main__':
    
    username = 'weibocir@126.com'
    pwd = 'weiboCirCir'
    cookie_file = 'weibo_login_cookies_wap.dat'
    
    if login(username, pwd, cookie_file, True):
        print 'Login WEIBO succeeded'
        #page = urllib2.urlopen('http://weibo.cn/cheungzee').read()
        #print page
    else:
        print 'Login WEIBO failed'
