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
item['note'] = '法学院'
item['INDEX'] = ['http://law.sysu.edu.cn']
item['DOMAIN'] = ['law.sysu.edu.cn']
item['LIST_URL_PATTERNS'] = []
item['ITEM_URL_PATTERNS'] = [r'/node/\d+$']
item['ITEM_TITLE_PATTERNS'] = ['//h1[@class="title"]/text()']
item['ITEM_CONTENT_PATTERNS'] = ['//div[@class="content clearfix"]']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'law'
item['LOG_FILE'] = '/tmp/logs/law.log'
item['last_crawl_time'] = time.time() - 12*3600
try:
    db.create_collection(item['TABLE'])
except pymongo.errors.CollectionInvalid:
    logging.info('the table %s has been created'% item['TABLE'])
    col.update({'INDEX': item['INDEX']}, item)
    logging.info('%s 更新成功'%item['note'])
else:
    col.insert(item)
    logging.info('%s 插入成功'%item['note'])

