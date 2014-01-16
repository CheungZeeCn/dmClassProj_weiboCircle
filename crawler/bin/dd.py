#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-11-30 16:52:56 
# Copyright 2013 NONE rights reserved.

import weibo_login
import conf
import util
import dataUtil
import urllib2
import surf_dev
import logging
import os
import pickle
import signal
import time

g_userResF = 'userRes.pickle'
g_userInfoF = 'userInfo.pickle'

g_out = set()
g_userRes = {}
g_userInfo = {}

def sig_exit():
    logging.info("[end time]:[%s]" % str(time.time()))
    logging.info("store g_userRes into %s"%(g_userResF))
    dump()
    logging.info("exit")
    sys.exit()

def handler(signum, frame):
    print "got an signal",signum,frame
    if signum == 3:
        sig_exit()
    if signum == 2:
        sig_exit()
    if signum == 9:
        sig_exit()
    return None
signal.signal(signal.SIGINT,handler)
signal.signal(signal.SIGTERM,handler)
signal.signal(3,handler)

def dump():
    global g_userInfoF, g_userInfo
    util.dump2Pickle(g_userInfo, g_userInfoF)

def load():
    global g_userRes, g_userResF, g_userInfoF, g_userInfo
    ret = util.loadPickle(g_userResF) 
    if ret == None:
        return {}, {}
    ret2 = util.loadPickle(g_userInfoF) 
    if ret2 == None:
        return ret, {}
    return ret, ret2

#def getSeedUser():
#    return g_userRes.keys()
def getSeedUser():
    #return g_userRes.keys()
    seeds = []
    with open('report/idList.list') as f:
        for l in f:
            l = l.strip()
            seeds.append(l)
    return seeds




if __name__ == '__main__':  
    g_userRes, g_userInfo = load()
    seeds = getSeedUser() 
    logging.info("load %d user res info" % (len(g_userRes.keys())))
    c = 0
    for seed in seeds:
        c += 1
        if seed in g_userInfo:
            logging.debug("%d/%d, user[%s] ignore" % (c, len(seeds), seed)) 
            continue
        g_userInfo[seed] = surf_dev.getUserInfo(seed)
        logging.debug("%d/%d, user[%s]" % (c, len(seeds), seed)) 
        print '===' * 30
        for each in g_userInfo[seed]:
            print each, util.psList(g_userInfo[seed][each])
    dump()
       
        

