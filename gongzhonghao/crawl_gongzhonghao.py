#!/usr/bin/env python
# coding=utf-8

import requests

class Response(object):
    """
    简单的http响应类
    """
    def __init__(self, body=None, url=None):
        self.body = body
        self.url = url

class CONST(object):
    """
    模拟宏定义
    """
    ARTICLE = 2
    GONGZHONGHAO = 1
    MONGO_HOSTNAME = '127.0.0.1'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'houyf'
    MONGO_PASSWORD = 'Beyond'
    MONGO_DATABASE =  'utipsV2'
    MONGO_COLLECTION = 'gongzhonghao'

class Item(dict):
    """
    消息类
    """
    def __init__(self):
        self.title = None
        self.digest = None
        self.crawl_time = None
        self.content = None 
        self.url = None 

def fetchSearchPage(query): 
    """
    根据query关键词获取搜狗微信文章搜索的页面内容
    query需要自己在搜狗微信搜索中试错过来确定，一般是目标对象的公众号
    """
    url = 'http://weixin.sogou.com/weixin'
    payload = {'type': CONST.ARTICLE, 'query': query}
    r = requests.get(url, params=payload)
    return Response(body=r.content, url=r.url)

def fetchArtPage(url):
    """
    获取文章页html
    """
    r = requests.get(url)
    return Response(body=r.content, url=r.url)

def getArtLinks(response):
    """
    获取http相应html页面的文章链接
    """
    from lxml import etree
    tree = etree.HTML(response.body)
    art_urls = tree.xpath('//div[@class="txt-box"]/h4/a/@href')
    return art_urls


def filterLinks(response):
    """
    过滤已经爬取过的文章
    """
    new_urls = getArtLinks(response)
    conn = connectionToMongo(
        host = CONST.MONGO_HOSTNAME, 
        port = CONST.MONGO_PORT, 
        username = CONST.MONGO_USERNAME,
        password = CONST.MONGO_PASSWORD,
        database = CONST.MONGO_DATABASE
    )
    db = conn['utipsV2']
    col = db['gongzhonghao']
    # 根据实际情况限制limit
    cursor = col.find({}, {'url':True})
    old_urls = list(cursor)
    old_urls = map(lambda i: i['url'], old_urls)
    urls_after_filter = []
    for url in new_urls: 
        if url not in old_urls:
            urls_after_filter.append(url)
    return urls_after_filter
    
def parseItem(response):
    """
    分析出文章各个字段
    """
    from lxml import etree
    tree = etree.HTML(response.body)
    item =Item()
    item['title'] = tree.xpath('//h2[@class="rich_media_title"]')[0]
    # __import__('pdb').set_trace()
    item['title'] = etree.tostring(item['title'], encoding='utf-8')
    item['content'] = tree.xpath('//div[@id="page-content"]')[0]
    item['content'] = etree.tostring(item['content'], encoding='utf-8')
    item['url'] = response.url
    return item
    
def connectionToMongo(host='localhost', port=27017, password=None, username=None, database=None):
    """
    封装简单的MongoDb的连接
    """
    uri = 'mongodb://{username}:{password}@{host}/{database}'.format(
        host=host, database=database, username=username, password=password
        )
    return __import__('pymongo').Connection(host=uri, port=port)

def before_save(item):
    """
    持久化保存前的预处理
    """
    item['crawl_time'] = __import__('time').time()

def saveItem(item):
    """
    保存文章到特定数据库
    """
    conn = connectionToMongo(
        host = CONST.MONGO_HOSTNAME, 
        port = CONST.MONGO_PORT, 
        username = CONST.MONGO_USERNAME,
        password = CONST.MONGO_PASSWORD,
        database = CONST.MONGO_DATABASE
    )
    db = conn['utipsV2']
    col = db['gongzhonghao']
    before_save(item)
    col.insert(item)
    return True
     

def crawl(target):
    """
    爬取的算法流程
    """
    SearchResponse = fetchSearchPage(target)
    new_urls = filterLinks(SearchResponse)
    for url in new_urls:
        response = fetchArtPage(url)
        item = parseItem(response)
        saveItem(item)



