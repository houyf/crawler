#!/usr/bin/env python
# coding=utf-8

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from utips.items import ArticleItem
from utips.functions import isArticle
from utips.functions import parseArticle
from utips.functions import LinkFilter
from scrapy.contrib.linkextractors import LinkExtractor

def getWebsitesFromMongodb():
    import pymongo
    conn = pymongo.Connection('127.0.0.1', 27017)
    db = conn['utipsV2']
    col = db['website']
    websites = set([site['index'] for site in col.find()])
    conn.close()
    return list(websites)

class Crawler(CrawlSpider):

    # start_urls = ['http://jwc.sysu.edu.cn/Item/8784.aspx']
    start_urls = getWebsitesFromMongodb()
    allowed_domains = ["jwc.sysu.edu.cn"]
    name =  'newCrawler'
    image_extensions = [
        '.mng', '.pct', '.bmp', '.gif', '.jpg', '.jpeg', '.png', '.pst', '.psp', '.tif',
        '.tiff', '.ai', '.drw', '.dxf', '.eps', '.ps', '.svg',
    ]
    file_extensions = [
        '.xls', '.xlsx', '.ppt', '.pptx', '.doc', '.docx', '.odt', '.ods', '.odg', '.odp',
    ]

    # log.start(loglevel=log.INFO)
    rules = [
        Rule(LinkExtractor(allow=(r'Index\.aspx')), follow = True, callback=None),
        Rule(LinkExtractor(allow=(r'\d+\.aspx')), follow = False, callback='parse_item', process_links='filterLinks'),
    ]

    def parse_item(self, response):
        log.msg('parsing the response', level=log.INFO) 
        if isArticle(response.url):
            log.msg('{url} is a Article'.format(url=response.url), level=log.INFO) 
            art = ArticleItem()
            if parseArticle(response, art):
                art['image_urls'] =  self.imageUrlsOfArticle(response)
                art['file_urls'] =  self.fileUrlsOfArticle(response)
                return art
            else:
                raise StopIteration
        else:
            raise StopIteration

    def filterLinks(self, links):
        return filter(LinkFilter.duplicate , links) 

    def imageUrlsOfArticle(self, contentSelc):        
        urls = contentSelc.xpath('//a[@href]/@href').extract()
        image_urls = []            
        for url in urls:
            for e in self.__class__.image_extensions:
                if url.find(e) != -1:
                    image_urls.append(url)
        return image_urls
                    
    def fileUrlsOfArticle(self, contentSelc):        
        urls = contentSelc.xpath('//a[@href]/@href').extract()
        file_urls = []            
        for url in urls:
            for e in self.__class__.file_extensions:
                if url.find(e) != -1:
                    file_urls.append(url)
        return file_urls
                
          
         









