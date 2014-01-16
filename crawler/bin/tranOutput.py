#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-12-02 22:26:11 
# Copyright 2013 NONE rights reserved.
inf1 = 'id_weiboId.txt'
inf = 'test.txt'

allOut = []

if __name__ == '__main__':
    id2WeiboId = {}
    with open(inf1) as f:
        lineList = f.read().split("\n")
        for line in lineList:
            line = line.strip()
            if line == '':
                continue
            line = line.split(" ")    
            id, weiboId = line
            id2WeiboId[id] = weiboId
    with open(inf) as f:
        for line in f:
            line = line.split(" ")
            out = []
            for id in line:
                id = id.strip()
                if id in id2WeiboId:
                    out.append(id2WeiboId[id])  
            allOut.append(out)
    allOut = sorted(allOut, lambda x, y: cmp(len(x), len(y)), reverse=True)
    for each in allOut:
        print " ".join(each)

