#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-12-05 11:58:04 
# Copyright 2013 NONE rights reserved.
"""
    从这两个文件导入内容
    wbWc = util.loadPickle('wbWc.pickle')
    infoWc = util.loadPickle('infoWc.pickle')
    分析这里面的前10个圈子的用户
    cList = loadCirecle('report/circles', 10) 
"""
import util
import math

def loadCirecle(fn, nu):
    cList = []
    with open(fn) as f:
        c = 0
        for l in f:
            if c >= nu: 
                break
            print l
            c += 1
            l = l.strip().split(" ")
            cList.append(l[1:])
    return cList

def addDict(a, b):
    for k in b:
        if k not in a:
            a[k] = 0
        a[k] += b[k]
    return a

def anaCircle(cInfoWcDict, cWbWcDict):
    infoIdf = {}
    wbIdf = {} 
    cTfInfo = countTf(cInfoWcDict)
    cTfWb = countTf(cWbWcDict)
    wIdfInfo = countIdf(cInfoWcDict)
    wIdfWb = countIdf(cWbWcDict)

    for cKey in cInfoWcDict:
        print "="*100
        print 'circle:', cKey
        print '-'*100
        print 'info:'
        print 'word count:'
        topN = util.getTopN(cInfoWcDict[cKey], 10)
        print  (", ".join([ '[%s:%s]'%(kv[0], kv[1]) for kv in topN])).encode('utf-8')
        print 'tf:'
        topN = util.getTopN(cTfInfo[cKey], 10)
        print  (" | ".join([ '[%s:%s]'%(kv[0], kv[1]) for kv in topN])).encode('utf-8')
        print 'tf.idf:'
        tfidf = countTfIdf(cTfInfo[cKey], wIdfInfo)
        topN = util.getTopN(tfidf, 10)
        print  (" | ".join([ '[%s:%s]'%(kv[0], kv[1]) for kv in topN])).encode('utf-8')
        print '-'*100
        print 'weibo:'
        print 'word count:'
        topN = util.getTopN(cWbWcDict[cKey], 10)
        print  (", ".join([ '[%s:%s]'%(kv[0], kv[1]) for kv in topN])).encode('utf-8')
        print 'tf:'
        topN = util.getTopN(cTfWb[cKey], 10)
        print  (" | ".join([ '[%s:%s]'%(kv[0], kv[1]) for kv in topN])).encode('utf-8')
        print 'tf.idf:'
        tfidf = countTfIdf(cTfWb[cKey], wIdfWb)
        topN = util.getTopN(tfidf, 10)
        print  (" | ".join([ '[%s:%s]'%(kv[0], kv[1]) for kv in topN])).encode('utf-8')

def countTfIdf(tf, idf):
    tfidf = {}
    for w in tf:
        tfidf[w] = float(tf[w]) * idf[w]
    return tfidf

def countTf(cWcDict):
    cTf = {}
    for c in cWcDict:
        tf = {}
        sumWc = sum([ cWcDict[c][w]  for w in cWcDict[c] ])
        for w in cWcDict[c]: 
            tf[w] = float(cWcDict[c][w])/sumWc
        cTf[c] = tf
    return cTf

def countIdf(cWcDict):
    idf = {} 
    D = len(cWcDict.keys()) 
    for c in cWcDict:
        for w in cWcDict[c]:
            if w not in idf:
                cnt = 0
                for cc in cWcDict:
                    if w in cWcDict[cc]:
                        cnt += 1
                idf[w] = math.log(float(D)/cnt, 2)
    return idf

if __name__ == '__main__':
    #load
    wbWc = util.loadPickle('wbWc.pickle')
    infoWc = util.loadPickle('infoWc.pickle')
    cList = loadCirecle('report/circles', 10) 
    cInfoWcDict = {}
    cWbWcDict = {}
    for c in cList:
        cKey = " ".join(c)
        cInfoWcDict[cKey] = {}
        cWbWcDict[cKey] = {}
        for u in c:
            addDict(cInfoWcDict[cKey], infoWc[u])
            addDict(cWbWcDict[cKey], wbWc[u])

    anaCircle(cInfoWcDict, cWbWcDict)


"""
        print "=" * 50
        print 'ciecle:', cKey
        print "info wc top 10"
        topN = util.getTopN(cInfoWcDict[cKey], 10)
        print " ".join([ '%s_%s'%(kv[0], kv[1]) for kv in topN])
        print "weibo wc top 10"
        topN = util.getTopN(cWbWcDict[cKey], 10)
        print " ".join([ '%s_%s'%(kv[0], kv[1]) for kv in topN])
"""
             
                     

