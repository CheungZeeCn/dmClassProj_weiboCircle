#!/usr/bin/env python
# encoding:utf8

import MySQLdb
from DBUtils.PooledDB import PooledDB
import conf
g_dbName = conf.dbName
g_dbUser = conf.dbUser
g_dbHost = conf.dbHost
g_dbPasswd = conf.dbPasswd
   
class dbOperator:
    def __init__(self):#填入你的数据库
        self.conn = PooledDB(MySQLdb, maxusage=1, db=g_dbName, host=g_dbHost, user=g_dbUser, passwd=g_dbPasswd, charset='utf8')

    def insert(self,value):
        pool = self.conn.connection()
        cursor = pool.cursor()
        #value = [None,pid,wbid,content,date]
        cursor.execute("insert into data values(%s,%s,%s,%s,%s)",value);
        cursor.close()
        pool.commit()
        pool.close()
        
    def insertRetweet(self,value):
        pool = self.conn.connection()
        cursor = pool.cursor()
        #value = [None,wbid,username,content,date]
        cursor.execute("insert into retweet values(%s,%s,%s,%s,%s)",value);
        cursor.close()
        pool.commit()
        pool.close()

    def updateName(self,upid,value):
        pool = self.conn.connection()
        cursor = pool.cursor()
        #value = [None,name,wbid,content,date]
        cursor.execute("UPDATE weibo_data SET name = \'%s\' WHERE wbid = \'%s\'" % (value,upid))
        cursor.close()
        pool.commit()
        pool.close()

    def selectData(self,sqlstr):
        pool = self.conn.connection()
        cursor = pool.cursor()    
        count = cursor.execute(sqlstr)
        results = cursor.fetchall()
        cursor.close()
        pool.close()
        return results
    
    def closeDb(self):
        self.conn.close()
        #self.conn = None
