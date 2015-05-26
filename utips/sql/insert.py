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
item['note'] = '中山大学新闻网 （content的元素是第三个p元素）'
item['INDEX'] = ['http://news2.sysu.edu.cn']
item['DOMAIN'] = ['news2.sysu.edu.cn']
item['LIST_URL_PATTERNS'] = [r'index\.htm']
item['ITEM_URL_PATTERNS'] = [r'\d{4,}\.htm']
item['ITEM_TITLE_PATTERNS'] = ['//h1/text()']
item['ITEM_CONTENT_PATTERNS']=['//div[@class="cont"]']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'news2'
item['LOG_FILE'] = '/tmp/logs/new2.log'
item['last_crawl_time'] = time.time() - 12*3600

try:
    db.create_collection(item['TABLE'])
except pymongo.errors.CollectionInvalid:
    logging.info('the table %s has been created'% item['TABLE'])
    col.update({'note': item['note']}, item)
    logging.info('%s 更新成功'%item['note'])
else:
    col.insert(item)
    logging.info('%s 插入成功'%item['note'])

