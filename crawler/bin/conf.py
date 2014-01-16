#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-11-30 16:03:47 
# Copyright 2013 NONE rights reserved.
import os

ROOTPATH = '/Users/cheungzee/opdir/dmClassProj_weiboCircle/crawler'
DATAPATH = os.path.join(ROOTPATH, 'data')
CONFPATH = os.path.join(ROOTPATH, 'conf')
OUTPATH = os.path.join(ROOTPATH, 'output')
cookiesPath ='/Users/cheungzee/opdir/dmClassProj_weiboCircle/crawler/conf'
loginConf = [ 
              ['weibocir@126.com', 'weiboCirCir'],\
              ['weibocir1@126.com', 'weiboCirCir'],\
              ['weibocir2@126.com', 'weiboCirCir'],\
              ['weibocir3@126.com', 'weiboCirCir'],\
              ['woshipachong@sina.cn', '123123a!'],\
]
dbName = 'weiboC'
dbUser = 'weiboC'
dbHost = '127.0.0.1'
dbPasswd = '123456'



cookieStoreBase = os.path.join(DATAPATH, 'cookies_store')
cookieStoreBaseWap = os.path.join(DATAPATH, 'cookies_store_wap')
proxyF = os.path.join(CONFPATH, 'proxy.txt')

if __name__ == '__main__':
    print 'hello world'

