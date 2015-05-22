# -*- coding: utf-8 -*-
import pymongo
import time
from scrapy.contrib.pipeline.images import ImagesPipeline, FilesPipeline
from scrapy import Request

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
        collection_name = item.__class__.__name__
        self.before_save_item(item)
        self.db[collection_name].insert(dict(item))
        return item

    def _replaceUrls(self, item):
        pass

    def before_save_item(self, item):
        item['crawl_time']  = time.time() 
        self._replaceUrls(item) 


class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['image_paths'] = image_paths
        return item

    
    def file_path(self, request, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)
        ## end of deprecation warning block

        image_guid = hashlib.sha1(url).hexdigest()  # change to request.url after deprecation
        return 'full/%s.jpg' % (image_guid)

class MyFilesPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        for file_url in item['file_urls']:
            yield Request(file_url)

    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        item['files'] = file_paths
        return item

    def file_path(self, request, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)
        ## end of deprecation warning block

        image_guid = hashlib.sha1(url).hexdigest()  # change to request.url after deprecation
        return 'full/%s.jpg' % (image_guid)
