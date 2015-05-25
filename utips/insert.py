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
item['note'] = '教务处'
item['INDEX'] = ['http://jwc.sysu.edu.cn/Index.aspx']
item['DOMAIN'] = ['jwc.sysu.edu.cn']
item['LIST_URL_PATTERNS'] = ['Index.aspx']
item['ITEM_URL_PATTERNS'] = [r'/Item/\d+\.aspx$']
item['ITEM_TITLE_PATTERNS'] = ['//h1[@class="art_title"]/text()']
item['ITEM_CONTENT_PATTERNS'] = ['//div[@class="content"]']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'jwc'
item['LOG_FILE'] = '/tmp/logs/jwc.log'
item['last_crawl_time'] = time.time() - 12*3600
try:
    db.create_collection(item['TABLE'])
except pymongo.errors.CollectionInvalid:
    logging.info('the table %s has been created'% item['TABLE'])
    
col.insert(item)
