#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-11-30 16:52:56 
# Copyright 2013 NONE rights reserved.
"""
    从下面两个文件中的内容
    uInfoDict = loadInfo('userInfo.pickle')     
    uWeiboDict = loadWeibo('weiboContent.txt', uList)
    生成
    util.dump2Pickle(wbWc, 'wbWc.pickle')
    util.dump2Pickle(infoWc, 'infoWc.pickle')
    供圈子分析使用
"""

import re
import weibo_login
import conf
import util
import dataUtil
import urllib2
#import surf_dev
import logging
import os
import pickle
import signal
import time
import json
import sys
import ltpservice
import unicodedata
import zhon


def dump(wbWc, infoWc):
    util.dump2Pickle(wbWc, 'wbWc.pickle')
    util.dump2Pickle(infoWc, 'infoWc.pickle')

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

def readJsonLine(f, data):
    data = json.dumps(data)
    f.write(data+"\n")
    f.flush()

def loadInfo(fn):
    return util.loadPickle(fn)

def loadWeibo(fn, uList=[]):
    retDict = {}
    with open(fn) as f:
        for l in f:
            j = json.loads(l)
            if j[0] not in uList and len(uList)!=0:
                continue 
            wb = j[1] 
            retDict[j[0]] = j[1]
    return retDict

def doWc(aList):
    wc = {}
    for e in aList:
        if e not in wc:
            wc[e] = 0
        wc[e] += 1
    return wc

def infoCountWc(userInfo):
    '''
    地区, 学习经历, 标签, 工作经历
    '''  
    wList = []
    if u'地区' in userInfo:
        wList += userInfo[u'地区']
    if u'标签' in userInfo:
        wList += userInfo[u'标签']
    if u'工作经历' in userInfo:
        for e in userInfo[u'工作经历']:
            a = " ".join(e[:-1])
            if a != '':
                wList += [a, e[-1]]
            else:
                wList += e
    if u'学习经历' in userInfo:
        for e in userInfo[u'学习经历']:
            a = " ".join(e[:-1])
            if a != '':
                wList += [a, e[-1]]
            else:
                wList += e
    return doWc(wList)

def noPunc(data):
    data = re.sub(ur'[%s]' % zhon.unicode.PUNCTUATION, " ", data)
    return data

def stripPunc(data):
    data = re.sub(ur'^[%s]' % zhon.unicode.PUNCTUATION, " ", data)
    data = re.sub(ur'[%s]$' % zhon.unicode.PUNCTUATION, " ", data)
    return data

def onlyCn(data):
    ret=''
    for e in data: 
        if unicodedata.category(e) == 'Lo':
            ret += e
    return ret

def pickN(client, data):
    Nlist = ['n', 'nh', 'ni', 'nl', 'ns', 'nz']
    result = None
    try:
        result = client.analysis(data.encode('utf-8'), ltpservice.LTPOption.POS) 
    except Exception, e:
        data = onlyCn(data)
        try:
            #print "###" * 30
            #print data
            #print "###" * 30
            result = client.analysis(data.encode('utf-8'), ltpservice.LTPOption.POS) 
        except Exception, e:
            # so sad
            #print 'so sad, data could not be handled==='
            #print data
            #print '========='*15
            pass

    if result == None:
        return []
    pid = 0
    ret = []
    re_empty = re.compile(ur"(\s| |)+")
    for sid in xrange(result.count_sentence(pid)):
        for w_p in result.get_words_and_pos(pid, sid):
            if w_p[1] in Nlist:
                r = unicode(w_p[0])
                r = re_empty.sub('', r) 
                r = stripPunc(r)
                r = r.strip(" ")
                r = stripSingle(r)
                if r != '':
                    #print "[%s|%s]" % (r, w_p[1])
                    ret.append(r)
    return ret

def stripSingle(w):
    if len(w) == 1:
        cw = onlyCn(w)
        if len(cw) == '':
            return ''
    return w

def countWord(client, data):
    wc = {}
    wList = pickN(client, data) 
    for nWord in wList:
        if nWord not in wc:
            wc[nWord] = 0
        wc[nWord] += 1
    return wc

def addDict(a, b):
    for k in b:
        if k not in a:
            a[k] = 0
        a[k] += b[k]
    return a

client = ltpservice.LTPService("%s:%s" % ('cheungzeecn@gmail.com', 'ncbh3oIf'))
def wbCountWc(weibo):
    global client
    step=20
    wc = {}
    for i in range(0, len(weibo), step):
        d = u"。".join(weibo[i:i+step])
        retWc = countWord(client, d)
        addDict(wc, retWc)
    return wc  
    

     


if __name__ == '__main__':  
    uList = ['/cheungzee']
    uWeiboDict = loadWeibo('weiboContent.txt')
    uInfoDict = loadInfo('userInfo.pickle')

    wbWcDict = {}
    infoWcDict = {}
    
    print len(uWeiboDict), len(uInfoDict), sum([ len(uWeiboDict[u])for u in uWeiboDict])
    
