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
item['note'] = '有代理网'
item['INDEX'] = [
    'http://www.youdaili.net/Daili/http/list_1.html',
    'http://www.youdaili.net/Daili/http/list_16.html', 
    'http://www.youdaili.net/Daili/http/list_26.html',
    ]
item['DOMAIN'] = ['www.youdaili.net']
item['LIST_URL_PATTERNS'] = [r'/Daili/http/list_\d+\.html']
item['ITEM_URL_PATTERNS'] = [r'/Daili/http/\d+\.html']
# 标题和文章的每一个匹配规则: 当匹配的是第一个节点时，不需要下标（为0）
# 当匹配的节点是有一定下标的节点时,使用列表形式记录
item['ITEM_TITLE_PATTERNS'] = ['//h1/text()']
item['ITEM_CONTENT_PATTERNS']=['//div[@class="cont_font"]/p/text()']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'youdaili'
item['LOG_FILE'] = '/tmp/logs/youdaili.log'
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

