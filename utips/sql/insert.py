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
item['note'] = '中大青年时空'
item['INDEX'] = ['http://zdtw.sysu.edu.cn/']
item['DOMAIN'] = ['zdtw.sysu.edu.cn']
item['LIST_URL_PATTERNS'] = [r'cat=']
item['ITEM_URL_PATTERNS'] = [r'p=\d+']
# 标题和文章的每一个匹配规则: 当匹配的是第一个节点时，不需要下标（为0）
# 当匹配的节点是有一定下标的节点时,使用列表形式记录
item['ITEM_TITLE_PATTERNS'] = ['//div[@class="title"]/text()', '//div[@class="title"]/text()']
item['ITEM_CONTENT_PATTERNS']=['//div[@class="content"]', '//div[@class="content clearfix"]']
item['SITE_ENCODING'] = 'utf-8' 
item['TABLE'] = 'zdtw'
item['LOG_FILE'] = '/tmp/logs/zdtw.log'
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

