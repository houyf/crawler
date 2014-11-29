# -*- coding: utf-8 -*-

# Scrapy settings for mySpider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

# sOT_NAME = 'mySpider'

# SPIDER_MODULES = ['mySpider.spiders']
# NEWSPIDER_MODULE = 'mySpider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent

BOT_NAME = 'mySpider'

SPIDER_MODULES = ['tmp.spiders']
NEWSPIDER_MODULE = 'tmp.spiders'
ITEM_PIPELINES = {
        # 'tmp.pipelines.MongoPipeline':2,
        'tmp.pipelines.MySQLStorePipeline':2,
        # 'scrapy.contrib.pipeline.images.ImagesPipeline':1,
        'tmp.pipelines.ImagesPipeline' :1,
}

#图片存放路径
IMAGES_STORE = '/home/houyf/crawler/mySpiderV2/images'
#图片失效日期，可以防止下载之前已经下载过的图片过的
IMAGES_EXPIRES = 90
#图片缩略图
# IMAGES_THUMBS = {
        # 'small': (50, 50),
        # 'big':(270, 270),
# }



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jwc (+http://www.yourdomain.com)'
# SCHEDULER_MIDDLEWARES_BASE = {
            # 'scrapy.contrib.schedulermiddleware.duplicatesfilter.DuplicatesFilterMiddleware': 500,
# }
# DUPEFILTER_DEBUG = True
DEPTH_LIMIT = 2
#默认是深度优先，一下可以设置为BFS
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'


MONGO_USR='houyf'
MONGO_PWD='Beyond'
MONGO_SERVER='localhost'
MONGO_PORT=27017
MONGO_DB='utipsV2'
