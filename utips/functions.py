#!/usr/bin/env python
# coding=utf-8
import re
from scrapy import log
_pattern_list = []

def isArticle(url):  
    for pattern in artUrlPatterns():
        matchObj = re.search(pattern, url, re.M|re.I)
        if matchObj:
            return True 
    return False

def parseArticle(response, art):
    try:
        if response.url.find('jwc.sysu.edu.cn') != -1:  
            log.msg('the news belongs to jwc.sysu.edu.cn', level=log.DEBUG) 
            art['title'] = response.xpath('//h1/text()')[0].extract()
            art['content'] = response.xpath('//div[@class="content"]')[0].extract()
            art['url'] = response.url
            log.msg('the news is parse successfully', level=log.DEBUG) 
            return True
        else:
            return False
    except IndexError:
        log.msg('the article is parse failly', level=log.ERROR)
        return False

def artUrlPatterns():
    if _pattern_list == []:
         _pattern_list.append(r'http://jwc\.sysu\.edu\.cn/Item/\d+\.aspx') 
    return _pattern_list


def getFilename(abspath, srcEncoding='utf-8', destEncoding='utf-8'):
    """
    接收一个附件的url
    返回相应的utf-8文件名
    """
    import os 
    from urllib import unquote
    return os.path.basename(unquote(abspath).decode(srcEncoding).encode(destEncoding))


class LinkFilter(object):
    
    _url_set = set()

    @classmethod
    def duplicate(cls, link):
        if cls._url_set == set():
            cls._url_set = cls._getUrlFromMongodb()
        if link.url not in cls._url_set:
            cls._url_set.add(link.url)
            log.msg('the news {url} has been crawled'.format(url=link.url), log.DEBUG)
            return True
        else:
            return False

    @classmethod
    def _getUrlFromMongodb(cls):
        import pymongo
        conn = pymongo.Connection('127.0.0.1', 27017)
        db = conn['utipsV2']
        col = db['ArticleItem']
        tmp_set = set([link['url'] for link in col.find()])
        conn.close()
        return tmp_set


from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse
from posixpath import normpath

def myUrljoin(base, url):
    """
        根据refer的url为base,　将相对url转为绝对url
    """
    url1 = urljoin(base, url)
    arr = urlparse(url1)
    path = normpath(arr[2])
    return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

