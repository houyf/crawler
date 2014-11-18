# encoding: utf-8
from scrapy import log
from scrapy import Spider
from scrapy import Request
from tmp.items import ArtItem
from tmp.items import UrlItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import re
import hashlib
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pymongo
from scrapy.conf import settings

class MySpider(CrawlSpider):

    def __init__(self):
        super(MySpider, self).__init__()
        # self.start_urls = self.startUrls()
        # self.allowed_domains = self.allowedDomains()
        self.conn = pymongo.Connection(settings['MONGO_SERVER'], settings['MONGO_PORT'])
        self.db = self.conn[settings['MONGO_DB']]
        self.col = self.db['c_urls']
        self.filter_urls = self.filterUrls()
        self.start_urls = self.test_startUrl()
        self.allowed_domains = self.test_allowedDomains()

    name = 'MySpider'

    def isArticle(self, url):

        pattern_list = [r'/(\d+)\..*', r'newsid', 'catid=\d+&id=\d+']
        pattern_list.append(r'ObjID=\d+&SubjectID=\d+') #im.sysu.edu.cn
        pattern_list.append(r'articleid=\d+') # gms.sysu.edu.cn
        pattern_list.append(r'pId=\d+&no=') #sist.sysu.edu.cn
        pattern_list.append(r'no=.*?&pId=\d+')
        pattern_list.append(r'CategoryID=\d+&TreeID=\d+&id=\d+') #yxjwc.sysu.edu.cn
        pattern_list.append(r'news_id=\d+') #bwc.sysu.edu.cn
        pattern_list.append(r'p=\d+') #http://zdtw.sysu.edu.cn
        pattern_list.append(r'id=\d+') #career.sysu.edu.cn
        pattern_list.append(r'news_id') #sanyushe.sysu.edu.cn
        pattern_list.append(r'announcement') #http://csirt.sysu.edu.cn

        for pattern in pattern_list:
            matchObj = re.search(pattern, url, re.M|re.I)
            if(matchObj != None) :
                return True
        return None

    def parse(self, response):
        # log.start(logfile='/home/houyf/logfile',loglevel=log.DEBUG)
        #hash and fielter
        urlhash = hashlib.md5(response.url.decode(response.encoding).encode('utf-8')).hexdigest()
        contenthash =  hashlib.md5(response.body.decode(response.encoding).encode('utf-8')).hexdigest()
        if(urlhash  in self.filter_urls and self.filter_urls[urlhash] == contenthash):
            print 'URL %s 内容没有发生改变 ' % response.url
            raise StopIteration

        #article
        if self.isArticle(response.url):
            print 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            item =  self.handleArt(response)
            if(item == None):
                raise StopIteration
            else :
                yield item

        #link to follow
        else :
            print 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU'
            urlList = self.getUrlList(response)
            for url in urlList:
                yield Request(url)
            # the url state also should be save to judge if modified next time
            item = UrlItem()
            item['url'] = response.url
            item['urlhash'] = hashlib.md5(response.url.decode(response.encoding).encode('utf-8')).hexdigest()
            item['contenthash'] = hashlib.md5(response.body.decode(response.encoding).encode('utf-8')).hexdigest()
            yield item
            raise StopIteration

    #从数据库获取开始url
    def startUrls(self):
        db = MySQLdb.connect(host="localhost", user="houyf", passwd="Beyond", db="utipsV2")
        cursor = db.cursor()
        cursor.execute('set names "utf8"')
        sql = 'select domain from c_seed limit 1'
        cursor.execute(sql)
        data = cursor.fetchall()
        list = []
        for row in data :
            url = self.fixedUrl(row[0])
            list.append(url)
        return list

    #抓取的域的范围
    def allowedDomains(self):
        db = MySQLdb.connect(host="localhost", user="houyf", passwd="Beyond", db="utipsV2")
        cursor = db.cursor()
        cursor.execute('set names "utf8"')
        sql = 'select domain from c_seed'
        cursor.execute(sql)
        data = cursor.fetchall()
        list = []
        for row in data :
            list.append(row[0])
        return list

    #选择url哈希和url对应内容的哈希，都是32位的字符串
    def filterUrls(self) :
        sql={}
        sql['urlhash'] = 1
        sql['contenturl'] = 1
        data = self.col.find()
        data = self.col.find({}, {'urlhash':1, 'contenthash':1})
        print data
        urlhash = {}
        for row in data :
            try:
                urlhash[row['urlhash']] = row['contenthash']
            except:
                print sys.exc_info()
                continue
        return urlhash


    def fixedUrl(self, url):
        if(url.find('http:') == -1):
            return  'http://' + url

    #handle the article url
    #return item
    def handleArt(self, response):
        url = response.url
        item = ArtItem()
        item['link'] = response.url
        item['urlhash'] = hashlib.md5(response.url.decode(response.encoding).encode('utf-8')).hexdigest()
        item['contenthash'] = hashlib.md5(response.body.decode(response.encoding).encode('utf-8')).hexdigest()

        if(url.find('http://jwc.sysu.edu.cn') != -1):
            art = response.xpath('//div[@class="art_content"]')[0]
            item['title'] = art.xpath('h1/text()').extract()[0]
            item['content'] = art.xpath('div[@class="content"]').extract()[0]

        elif(url.find('xsc2000.sysu.edu.cn') != -1) :
            try :
                item['title'] = response.xpath('//*[@class="tit"]/text()').extract()[0]
                item['content'] = response.xpath('//*[@class="MsoNormal"]/parent::*').extract()[0]
            except:
                print '该URL不是文章'
                return None

        elif(url.find('law.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//*[@id="article_title"]/text()').extract()[0]
            item['content'] = response.xpath('//*[@id="article_content"]').extract()[0]

        elif(url.find('bus.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@class="cons"]/h3/text()').extract()[0]
            item['content'] = response.xpath('//div[@class="cons_detail"]').extract()[0]

        elif(url.find('egs.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//h1')[0].extract()
            item['content'] = response.xpath('//*[@id="text"]')[0].extract()

        elif(url.find('ss.sysu.edu.cn') != -1) :
            item['title'] =  response.xpath('//div[@class="article"]/div[@class="articleTitle"]')[0].extract()
            item['content'] = response.xpath('//div[@class="article"]/div[@class="articleContent"]')[0].extract()

        elif(url.find('scd.sysu.edu.cn') != -1) :
            item['title'] =  response.xpath('//*[@class="ArtTitle"]/text()')[0].extract()
            item['content'] = response.xpath('//*[@class="ArtCont"]')[0].extract()

        elif(url.find('zssom.sysu.edu.cn') != -1) :
            item['title'] =  response.xpath('//div[@class="cons article"]/h3/text()')[0].extract()
            item['content'] = response.xpath('//div[@class="cons_detail"]')[0].extract()

        # 我去，是gbk编码
        # elif(url.find('www.zdkqyy.com') != -1) :
            # item['title'] =  response.xpath('//tr')[1].xpath('td')[0].xpath('div')[0].xpath('div')[1]
            # item['content'] = response.xpath('//tr')[1].xpath('td')[0].xpath('div')[0].xpath('div')[2]

        elif(url.find('sps.sysu.edu.cn') != -1) :
            item['title'] =   response.xpath('//div[@class="contWrap"]/h2/text()')[0].extract()
            item['content'] = response.xpath('//div[@class="contWrap"]/div[@class="cont"]')[0].extract()

        #我去，这个真够坑爹, gbk
        elif(url.find('im.sysu.edu.cn') != -1) :
            item['title'] =  response.xpath('/html/body/table')[1].xpath('tbody/tr')[1].xpath('td/table/tr/td/font/strong/text()')[0].extract()
            item['content'] = response.xpath('/html/body/table')[1].xpath('tbody/tr')[1].xpath('td/table/tr')[2].xpath('td/span')[0].extract()

        #我擦，网络中心你他们能规范下文章url命名吗？
        # elif(url.find('helpdesk.sysu.edu.cn/') != -1) :

        elif(url.find('news2.sysu.edu.cn') != -1) :
            item['title'] =  response.xpath('//div[@class="cont"]/h1/text()')[0].extract()
            item['content'] = response.xpath('//div[@class="cont"]/p')[1].extract()


        # js
        # elif(url.find('card.sysu.edu.cn') != -1) :
            # item['title'] =   response.xpath('//*[@id="title"]')[0].extract()
            # item['content'] = response.xpath('//*[@id="content"]')[0].extract()


        elif(url.find('gms.sysu.edu.cn') != -1) :
            item['title'] =   response.xpath('//*[@class="cattitle2"]')[0].extract()
            item['content'] = response.xpath('//*[@class="content"]')[0].extract()

        #the site can't open nima
        # elif(url.find('sese.sysu.edu.cn') != -1) :

        elif(url.find('sist.sysu.edu.cn') != -1) :
            try:
                item['title'] =   response.xpath('//b/font[@size="3"]')[0].extract()
                item['content'] = response.xpath('//*[@class="MsoNormal"]')[0].xpath('parent::*')[0].extract()
            except:
                print '%s Not an article' %response.url
                return None

        elif(url.find('nursing.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//*[@class="title2"]/text()')[0].extract()
            item['content'] = response.xpath('//*[@class="bd"]')[0].extract()

        #holly shit
        # elif(url.find('gwxy.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//*[@class="title2"]/text()')[0].extract()
            # item['content'] = response.xpath('//*[@class="bd"]')[0].extract()

        #这个坑爹,文章居然没有统一的结构, 好像是子分类都有各自的文章样式
        #http://lifescience.sysu.edu.cn/main/news/news.aspx?pId=113&no=83e44c3b-6fbe-4098-aff5-7569d15bc6a3
        #http://lifescience.sysu.edu.cn/main/news/news.aspx?pId=31&no=d23e3d8b-3d8d-4051-bf3e-e454ef6c0158
        elif(url.find('lifescience.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//b/font[@size="5"]')[0].extract()
            item['content'] = response.xpath('//*[@class="MsoNormal"]/parent::*')[0].extract()

        elif(url.find('nursing.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//*[@class="title2"]/text()')[0].extract()
            item['content'] = response.xpath('//*[@class="bd"]')[0].extract()

        #跟我说建设中，呵呵
        # elif(url.find('home3.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//*[@class="title2"]/text()')[0].extract()
            # item['content'] = response.xpath('//*[@class="bd"]')[0].extract()

        elif(url.find('med.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@id="cont"]/h3/text()')[0].extract()
            item['content'] = response.xpath('//div[@id="cont"]')[0].extract()

        #草居然有些font size 还有　3 和　４　的
        elif(url.find('yxjwc.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@class="title"]')[0].extract()
            item['content'] = response.xpath('//font[@size]')[0].extract()

        elif(url.find('www.aijingsai.com') != -1) :
            item['title'] = response.xpath('//div[@id="content"]/h1/text()')[0].extract()
            item['content'] =  response.xpath('//div[@id="content"]/*[@class="content"]')[0].extract()

        #ajax
        # elif(url.find('east.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//div[@class="main_container"]/h1/text()')[0].extract()
            # item['content'] =  response.xpath('//div[@class="main_container"]')[0].extract()

        elif(url.find('bwc.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@class="title_news"]/span/text()')[0].extract()
            item['content'] =  response.xpath('//div[@id="divNewsContent"]')[0].extract()

        elif(url.find('hq.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@id="cont"]/h1/text()')[0].extract()
            item['content'] =  response.xpath('//div[@id="cont"]')[0].extract()

        elif(url.find('graduate.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@id="cont"]/h1/text()')[0].extract()
            item['content'] =  response.xpath('//div[@id="cont"]')[0].extract()


        #kakakakakakakkaka
        # elif(url.find('hemclecture.org') != -1) :
            # item['title'] = response.xpath('//div[@id="cont"]/h1/text()')[0].extract()
            # item['content'] =  response.xpath('//div[@id="cont"]')[0].extract()

        #content, content clearfix
        elif(url.find('zdtw.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//*[@class="title"]/text()')[0].extract()

            item['content'] =  response.xpath('//*[@class="content"]')
            if(len(item['content'] ) != 0):
                item['content'] = item['content'][0].extract()
            else :
                item['content'] = response.xpath('//*[@class="content clearfix"]')[0].extract()

        # ok i give up
        elif(url.find('skc.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//div[@id="cont"]/h1/text()')[0].extract()
            item['content'] =  response.xpath('//div[@id="cont"]')[0].extract()

        elif(url.find('career.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//*[@class="td_title"]')[0].extract()
            item['content'] =  response.xpath('//td[@class="mainbox"]/div')[0].extract()


        #ajax
        # elif(url.find('lecture.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//div[@id="news_tittle"]/h1/text()')[0].extract()
            # item['content'] = response.xpath('//div[@id="news_content"]')[0].extract()

        #js
        # elif(url.find('sanyushe.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//div[@id="news_tittle"]/h1/text()')[0].extract()
            # item['content'] = response.xpath('//div[@id="news_content"]')[0].extract()

        # not all
        elif(url.find('study.sysu.edu.cn') != -1) :
            item['title'] = response.xpath('//*[@class="rneirong2"]/p/span/text()')[0].extract()
            item['content'] =  response.xpath('//*[@class="MsoNormal"]')[0].extract()

        # elif(url.find('csirt.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//*[@class="rneirong2"]/p/span/text()')[0].extract()
            # item['content'] =  response.xpath('//*[@class="MsoNormal"]')[0].extract()

        # elif(url.find('study.sysu.edu.cn') != -1) :
            # item['title'] = response.xpath('//*[@class="rneirong2"]/p/span/text()')[0].extract()
            # item['content'] =  response.xpath('//*[@class="MsoNormal"]')[0].extract()
        else :
            return None
        return item

    #get all links of the  page
    def getUrlList(self, response):
        base_url = get_base_url(response)
        urlList = response.xpath('//a/@href').extract()
        abs_urlList = []
        filter = ['pdf', 'jpg', 'jpeg', 'gif', 'doc', 'docx']
        for rel_url in urlList:
            b = True
            for str in filter :
                if(rel_url.find(str) != -1):
                    b = False
                    break
            if(b):
                abs_urlList.append(urljoin_rfc(base_url, rel_url))

        return abs_urlList


###################TEST#####################
    def test_startUrl(self):
        return ['http://csirt.sysu.edu.cn']

    def test_allowedDomains(self):
        return ['csirt.sysu.edu.cn']
