# -*- coding: utf-8 -*-
import pymongo
import time
from scrapy.contrib.pipeline.images import ImagesPipeline, FilesPipeline
from config import ConfigContainer

class MongoStorePipeline(object):
    
    def __init__(self, hostname, database):
        self.hostname = hostname
        self.database = database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            hostname = crawler.settings.get('MONGO_HOSTNAME'), 
            database = crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.hostname)
        self.db = self.client[self.database]

    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        collection_name = ConfigContainer.getWebsiteConfig('TABLE')
        self.before_save_item(item)
        data = dict(item)
        if data.get('image_urls') is not None:
            data.pop('image_urls')
        if data.get('image_paths')is not None:
            data.pop('image_paths')
        if data.get('file_urls') is not None:
            data.pop('file_urls')
        if data.get('files') is not None:
            data.pop('files')
        self.db[collection_name].insert(data)
        return item

    def _replaceUrls(self, item):
        pass

    def before_save_item(self, item):
        item['isHandled'] = False
        item['crawl_time']  = time.time()  
        self._replaceUrls(item) 

class MyImagesPipeline(ImagesPipeline):
    
    def file_path(self, request, response=None, info=None):

        from urllib import unquote
        import os
        image_name = os.path.basename(unquote(request.url).decode('utf-8').encode('utf-8'))
        return image_name
        #  image_guid = request.url.split('/')[-1]
        #  return 'full/%s' % (image_guid)

class MyFilesPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None):
        from urllib import unquote
        import os
        filename = os.path.basename(unquote(request.url).decode('utf-8').encode('utf-8'))
        return filename
        #  image_guid = request.url.split('/')[-1]
        #  return 'full/%s' % (image_guid)


