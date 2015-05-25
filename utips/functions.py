#!/usr/bin/env python
# coding=utf-8
from scrapy import log
from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse
from posixpath import normpath
from config import ConfigContainer


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
        col = db[ConfigContainer.getWebsiteConfig('TABLE')]
        tmp_set = set([link['url'] for link in col.find()])
        conn.close()
        return tmp_set


def myUrljoin(base, url):
    """
        根据refer的url为base,　将相对url转为绝对url
    """
    url1 = urljoin(base, url)
    arr = urlparse(url1)
    path = normpath(arr[2])
    return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

