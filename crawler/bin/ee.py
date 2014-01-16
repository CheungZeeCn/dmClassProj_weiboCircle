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
import json

g_userResF = 'userRes.pickle'
g_userDoneF = 'userDone.pickle'

g_userRes = {}
g_userDone = set()

g_oF = None
g_oF = 'weiboContent.txt'

g_c = 0
g_storeStep = 30
def autoStore():
    global g_c, g_storeStep
    last = g_c / g_storeStep
    g_c += 1   
    if g_c / g_storeStep > last:
        logging.debug("auto dump len(g_userDone):%s" % (len(g_userDone))) 
        dump()

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
    global g_userDoneF, g_userDone, gf
    util.dump2Pickle(g_userDone, g_userDoneF)
    try:
        gf.flush()
    except Exception, e:
        logging.error("e")

def load():
    global g_userRes, g_userResF, g_userDoneF, g_userDone
    ret = util.loadPickle(g_userResF) 
    if ret == None:
        return {}, []
    ret2 = util.loadPickle(g_userDoneF) 
    if ret2 == None:
        return ret, []
    return ret, ret2

def getSeedUser():
    #return g_userRes.keys()
    seeds = []
    with open('report/idList.list') as f:
        for l in f:
            l = l.strip()
            seeds.append(l)
    return seeds

def appendJson(f, data):
    data = json.dumps(data)
    f.write(data+"\n")
    f.flush()


if __name__ == '__main__':  
    gf = open(g_oF, 'a')
    g_userRes, g_userDone = load()
    seeds = getSeedUser() 
    logging.info("load %d user res info" % (len(g_userRes.keys())))
    c = 0
    for seed in seeds:
        c += 1
        if seed in g_userDone:
            logging.debug("%d/%d, user[%s] ignore" % (c, len(seeds), seed)) 
            continue
        contents = surf_dev.getUserContent(seed, 10)
        logging.debug("%d/%d, user[%s] got weibo(%d)" % (c, len(seeds), seed, len(contents))) 
        out = [seed, contents]
        appendJson(gf, out)
        g_userDone.append(seed)
        autoStore()
    dump()
       

        

