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

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
    'utips.middlewares.RotateUserAgentMiddleware' :400,
    'utips.middlewares.ProxyMiddleware' :401
}

USER_AGENT_LIST= [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
    "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
   ]

HTTP_PROXY='http://127.0.0.1:8123'

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

# 禁止重试
RETRY_ENABLED = False
# 设置下载超时
DOWNLOAD_TIMEOUT = 15
# 禁止重定向
REDIRECT_ENABLED = False
