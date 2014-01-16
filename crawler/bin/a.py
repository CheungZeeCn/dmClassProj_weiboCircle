#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-12-04 23:13:56 
# Copyright 2013 NONE rights reserved.
import urllib
import urllib2

chinese_text = """
这里填上需要分词的文本

"""

_SEGMENT_BASE_URL = 'http://segment.sae.sina.com.cn/urlclient.php'

payload = urllib.urlencode([('context', chinese_text),])
args = urllib.urlencode([('word_tag', 1), ('encoding', 'UTF-8'),])
url = _SEGMENT_BASE_URL + '?' + args
result = urllib2.urlopen(url, payload).read()
print result


