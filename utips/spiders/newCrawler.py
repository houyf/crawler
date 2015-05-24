#!/usr/bin/env python
# coding=utf-8

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from utips.items import ArticleItem
from utips.functions import LinkFilter
import utips.settings as settings
from scrapy.contrib.linkextractors import LinkExtractor
from utips.functions import myUrljoin


def getWebsitesFromMongodb():
    import pymongo
    conn = pymongo.Connection(settings.MONGO_SERVER, settings.MONGO_PORT)
    db = conn[settings.MONGO_DATABASE]
    col = db['website']
    websites = set([site['index'] for site in col.find()])
    conn.close()
    return list(websites)

class Crawler(CrawlSpider):

    start_urls = [settings.INDEX] 
    allowed_domains = [settings.DOMAIN]
    name =  'websiteSpider'

    rules = [
        Rule(LinkExtractor(allow=settings.LIST_URL_PATTERNS), follow = True, callback=None),
        Rule(LinkExtractor(allow=settings.ITEM_URL_PATTERNS), follow = False, callback='parse_item', process_links='filterLinks'),
    ]

    def __init__(self):
        super(self.__class__, self).__init__()
        # log.start(loglevel=log.INFO)

    def parse_item(self, response):
        log.msg('parsing the response', level=log.INFO) 
        art = ArticleItem()
        try:
            log.msg('the news belongs to jwc.sysu.edu.cn', level=log.DEBUG) 
            contentSel = response.xpath('//div[@class="content"]')[0]
            titleSel = response.xpath('//h1/text()')[0]
            log.msg('the news is parse successfully', level=log.DEBUG) 
        except IndexError:
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

