#!/usr/bin/env python
# coding=utf-8

import pymongo
conn = pymongo.Connection('localhost', 27017)
db = conn['utipsV2']
col = db['website']
item = {}

item['id']  = 1
item['note'] = '教务处'
item['INDEX'] = 'http://jwc.sysu.edu.cn/Index.aspx'
item['DOMAIN'] = 'jwc.sysu.edu.cn'
item['LIST_URL_PATTERNS'] = [r'/Index\.aspx']
item['ITEM_URL_PATTERNS'] = [r'/\d+\.aspx']
item['ITEM_TITLE_PATTERNS'] = ['//h1/text()']
item['ITEM_CONTENT_PATTERNS'] = ['//div[@class="content"]']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'jwc'
item['LOG_FILE'] = '/tmp/logs/jwc.log'
col.remove()
col.insert(item)
