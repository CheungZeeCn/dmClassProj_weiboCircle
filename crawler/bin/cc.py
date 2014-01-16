#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-11-30 16:52:56 
# Copyright 2013 NONE rights reserved.

import weibo_login
import conf
import util
import dataUtil
import urllib2
import surf
import logging
import os
import pickle
import signal
import time

g_userResF = 'userRes.pickle'

g_out = set()
g_userRes = {}

g_c = 0
g_storeStep = 30
def autoStore():
    global g_c, g_storeStep
    last = g_c / g_storeStep
    g_c += 1   
    if g_c / g_storeStep > last:
        logging.debug("auto dump len(g_userRes.keys()):%s" % (len(g_userRes.keys()))) 
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
    global g_userRes, g_userResF
    if g_userRes != {}:
        util.dump2Pickle(g_userRes, g_userResF)

def load():
    global g_userRes, g_userResF
    ret = util.loadPickle(g_userResF) 
    if ret == None:
        return {}
    return ret

def addInOutput(user, biIds):
    for each in biIds:
        g_out.add((user, each))
        # do this for sinaWeibo's lock
        g_out.add((each, user))

def getSeedUser():
    ret = dataUtil.getSeedUserList()
    userList = [ x[2] for x in ret  ]
    return userList

def dumpRes():
    for u in g_userRes:
        biIds = [ bi[0] for bi in g_userRes[u][2] ]
        addInOutput(u, biIds) 
    with open('output_bi.txt', 'w') as f:
        for each in g_out:
            f.write(("%s\t%s\n" % (each[0], each[1])).encode('utf-8'))
        

if __name__ == '__main__':  
    seeds = getSeedUser() 
    g_userRes = load()
    logging.info("load %d user res info" % (len(g_userRes.keys())))
    for seed in seeds:
        flwrs, flwees, bis = surf.getUserFollower(seed)
        g_userRes[seed] = (flwrs, flwees, bis)
        level1 = bis
        biIds = [ each[0] for each in bis ]
        addInOutput(seed, biIds) 
        level2 = [] 
        for l1 in level1:
            if l1[0] in g_userRes:
                logging.debug("[%s] in g_userRes, ignore"%l1[0])
                bis1 = g_userRes[l1[0]][2]
                level2 += bis1
                continue
            flwrs1, flwees1, bis1 = surf.getUserFollower(l1[0])
            autoStore()
            level2 += bis1
            g_userRes[l1[0]] = (flwrs1, flwees1, bis1)
            biIds = [ each[0] for each in bis1 ]
            addInOutput(l1[0], biIds) 
            logging.debug("%d userResGot" % len(g_userRes))
        

        level2 = list(set(level2))
        level3 = [] # do nothing here
        for l2 in level2:
            if l2[0] in g_userRes:
                logging.debug("[%s] in g_userRes, ignore"%l2[0])
                continue
            flwrs2, flwees2, bis2 = surf.getUserFollower(l2[0])
            autoStore()
            level3 += bis2
            g_userRes[l2[0]] = (flwrs2, flwees2, bis2)
            bisIds = [ each[0] for each in bis2 ]
            addInOutput(l2[0], biIds) 
            logging.debug("%d userResGot" % len(g_userRes))

    dump()
    dumpRes()          
       
        

