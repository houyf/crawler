# -*- coding: utf-8 -*-

# Scrapy settings for newCrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'utips'

SPIDER_MODULES = ['utips.spiders']
NEWSPIDER_MODULE = 'utips.spiders'


ITEM_PIPELINES = {
    'utips.pipelines.MyImagesPipeline': 1,
    'utips.pipelines.MyFilesPipeline': 2,
    # 'scrapy.contrib.pipeline.images.ImagesPipeline': 1,
    # 'scrapy.contrib.pipeline.images.FilesPipeline': 2,
    'utips.pipelines.MongoStorePipeline': 800,
}

# database config 
MONGO_HOSTNAME = '127.0.0.1'
MONGO_DATABASE = 'utipsV2'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'newCrawler (+http://www.yourdomain.com)'

DEPTH_LIMIT = 2

COOKIES_ENABLED = False

IMAGES_STORE = '/home/houyf/Projects/crawler/utips/images'
IMAGES_EXPIRES = 90
IMAGES_DOMAIN = 'http://42.121.129.102:8089/crawl_images'
FILES_STORE='/home/houyf/Projects/crawler/utips/files'
