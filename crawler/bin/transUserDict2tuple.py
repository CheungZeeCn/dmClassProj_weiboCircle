#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-11-30 16:52:56 
# Copyright 2013 NONE rights reserved.

import weibo_login
import conf
import util
import dataUtil
import urllib2
#import surf
import logging
import os
import pickle
import signal
import time

# for qingfan
g_name2Id = {}
g_id2Name = []
def getUserCode(name):
    if name in g_name2Id:
        return g_name2Id[name]
    else:
        g_name2Id[name] = len(g_id2Name)
        g_id2Name.append(name)
        return g_name2Id[name]

g_userResF = 'userRes.pickle'

g_out = set()
g_userRes = {}

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
    with open('output_bi.txt', 'w') as f:
        for each in g_out:
            c0 = getUserCode(each[0])
            c1 = getUserCode(each[1])
            f.write(("%s %s\n" % (c0, c1)).encode('utf-8'))

    with open('id_weiboId.txt', 'w') as f:
        for i in range(len(g_id2Name)):
            f.write(("%s %s\n" % (i, g_id2Name[i])).encode('utf-8'))
            
            


if __name__ == '__main__':  
    g_userRes = load()
    print "keys:", g_userRes.keys()
    print "len keys:", len(g_userRes.keys())
    for user in g_userRes:
        bis = g_userRes[user][2]
        biIds = [ x[0] for x in bis ]
        addInOutput(user, biIds)
    dumpRes()          
       
        

