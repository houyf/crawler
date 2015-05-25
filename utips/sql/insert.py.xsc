#!/usr/bin/env python
# coding=utf-8

import time
import pymongo
import logging


logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filemode='w')

conn = pymongo.Connection('localhost', 27017)
db = conn['utipsV2']
col = db['website']
item = {}
item['id']  = 2
item['note'] = '学生处'
item['INDEX'] = ['http://xsc.sysu.edu.cn/zh-hans']
item['DOMAIN'] = ['xsc.sysu.edu.cn']
item['LIST_URL_PATTERNS'] = [r'/[a-zA-Z]{2,5}$']
item['ITEM_URL_PATTERNS'] = [r'/node/\d+$']
item['ITEM_TITLE_PATTERNS'] = ['//h1[@class="title"]/text()']
item['ITEM_CONTENT_PATTERNS'] = ['//div[@class="content-middle"]']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'xsc'
item['LOG_FILE'] = '/tmp/logs/xsc.log'
item['last_crawl_time'] = time.time() - 12*3600
try:
    db.create_collection(item['TABLE'])
except pymongo.errors.CollectionInvalid:
    logging.info('the table %s has been created'% item['TABLE'])
    
col.insert(item)
