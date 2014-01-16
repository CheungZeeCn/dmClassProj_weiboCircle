#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-12-03 21:15:15 
# Copyright 2013 NONE rights reserved.

from bs4 import BeautifulSoup as B
from bs4 import BeautifulSoup 
import re
import json
import string
import zhon

def noPunc(data):
    data = re.sub(ur'[%s]' % zhon.unicode.PUNCTUATION, " ", data)   
    return data

            
if __name__ == '__main__':
    data = open('/tmp/t').read()
    data = json.loads(data.strip())
    name = data[0]
    weibo = data[1]
    data = "|".join(weibo)
    data = noPunc(data)
    print data
