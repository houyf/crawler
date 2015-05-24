#!/usr/bin/env python
# coding=utf-8

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from utips.items import ArticleItem
from utips.functions import LinkFilter
import utips.settings as settings
from scrapy.contrib.linkextractors import LinkExtractor
from utips.functions import myUrljoin
from time import time
import pymongo


def fetchOneWebsiteConfig():
    conn = pymongo.Connection(settings.MONGO_SERVER, settings.MONGO_PORT)
    db = conn[settings.MONGO_DATABASE]
    col = db['website']
    website_config = col.find_one({'last_crawl_time':{'$lt': time()-12*3600}})
    if not website_config:
        website_config = {}
        website_config['LIST_URL_PATTERNS'] = []
        website_config['ITEM_URL_PATTERNS'] = []
        website_config['INDEX'] = []
        website_config['DOMAIN'] = []
        website_config['ITEM_TITLE_PATTERNS'] = []
        website_config['ITEM_CONTENT_PATTERNS'] = []
    else:
        col.update({'_id':website_config['_id']}, {'last_crawl_time':time()})

    return website_config

class Crawler(CrawlSpider):

    name =  'websiteSpider'
    website_config = fetchOneWebsiteConfig()
    rules = [
        Rule(LinkExtractor(allow=website_config['LIST_URL_PATTERNS']), follow = True, callback=None),
        Rule(LinkExtractor(allow=website_config['ITEM_URL_PATTERNS']), follow = False, callback='parse_item', process_links='filterLinks'),
    ] 
    start_urls = website_config['INDEX']
    allowed_domains = website_config['DOMAIN']

    def __init__(self):
        super(self.__class__, self).__init__()
        if settings.__dict__.get('LOG_ENABLED') :
            log.start(logfile=self.__class__.website_config.get('LOG_FILE', 'log'), loglevel=log.INFO)

    def parse_item(self, response):
        log.msg('parsing the response', level=log.INFO) 
        art = ArticleItem()
        log.msg('the news belongs to {domain}'.format(domain=self.__class__.website_config['DOMAIN']), level=log.DEBUG) 
        matched = False
        for tp, cp in zip(self.__class__.website_config['ITEM_TITLE_PATTERNS'], self.__class__.website_config['ITEM_CONTENT_PATTERNS']):
            try:
                contentSel = response.xpath(tp)[0]
                titleSel = response.xpath(cp)[0]
                log.msg('the news is parse successfully', level=log.DEBUG) 
                matched = True
                break
            except IndexError:
                continue; 
        if not matched:
            log.msg('the article {url}  is parse failly'.format(url=response.url), level=log.ERROR)
            raise StopIteration

        art['title'] = titleSel.extract()
        art['content'] = contentSel.extract()
        art['url'] = response.url
        art['image_urls'] =  self.imageUrlsOfArticle(contentSel, response)
        art['file_urls'] =  self.fileUrlsOfArticle(contentSel, response)
        return art

    def filterLinks(self, links):
        return filter(LinkFilter.duplicate , links) 

    def imageUrlsOfArticle(self, contentSelc, response):        
        urls = contentSelc.xpath('//a[@href]/@href').extract()
        image_urls = []            
        for url in urls:
            for e in settings.IMAGE_EXTENSIONS:
                if url.find(e) != -1:
                    url = myUrljoin(response.url, url)
                    image_urls.append(url)
        return image_urls
                    
    def fileUrlsOfArticle(self, contentSelc, response):        
        urls = contentSelc.xpath('//a[@href]/@href').extract()
        file_urls = []            
        for url in urls:
            for e in settings.FILE_EXTENSIONS:
                if url.find(e) != -1:
                    url = myUrljoin(response.url, url)
                    file_urls.append(url)
        return file_urls


def getWebsitesFromMongodb():
    import pymongo
    conn = pymongo.Connection(settings.MONGO_SERVER, settings.MONGO_PORT)
    db = conn[settings.MONGO_DATABASE]
    col = db['website']
    websites = set([site['index'] for site in col.find()])
    conn.close()
    return list(websites)
