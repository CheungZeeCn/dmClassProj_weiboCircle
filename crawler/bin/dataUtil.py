#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-12-01 10:35:18 
# Copyright 2013 NONE rights reserved.
import dbOperP
import conf

def getSeedUserList():
        dbo = dbOperP.dbOperator()
        results = dbo.selectData("select id, uName, Wid from seed_users")
        dbo.closeDb()
        return results

if __name__ == '__main__':
    print getSeedUserList()

