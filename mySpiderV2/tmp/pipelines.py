# encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from tmp.items import ArtItem
from tmp.items import UrlItem
from scrapy import log
from scrapy.exceptions import DropItem
import select
import errno
import hashlib
import datetime
import pymongo
from  scrapy.conf import settings


#连接数据库
class MongoPipeline(object):
    def __init__(self):
        self.conn = pymongo.Connection(settings['MONGO_SERVER'], settings['MONGO_PORT'])
        self.db = self.conn[settings['MONGO_DB']]
        self.db.authenticate(settings['MONGO_USR'], settings['MONGO_PWD'])
        self.col_content = self.db['c_all_text']
        self.col_ref = self.db['c_urls']
        self.urlhash = self.setUrlhash()

    #pipeline默认调用
    def process_item(self, item, spider):
        # if not the article
        if (isinstance(item, UrlItem)):
            # update or insert the UrlItem
            if(item['urlhash']  in self.urlhash):
                print '1111111111111111111111111111111111'
                self.updateUrlItem(item)
            else :
                print '22222222222222222222222222'
                self.insertUrlItem(item)

        #if is the article
        else :
            #对item的title和content 格式化处理
            item['title'] = item['title'].replace('"', '\"')
            item['title'] = item['title'].replace("'", "\'")
            item['content'] = item['content'].replace('"', '\"')
            item['content'] = item['content'].replace("'", "\'")

            # 如果没有数据库没记录，则作为新文章插入
            if( item['urlhash']  not  in self.urlhash) :
                print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
                self.insertArtItem(item)
            #如果内容被修改，则修改原文章，但是发布时间别变
            elif item['contenthash'] != self.urlhash[item['urlhash']]:
                print 'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW'
                self.updateArtItem(item)
        return item

    def insertArtItem(self, item):
        try :
            # insert into c_all_text
            sql = {}
            sql['title'] = item['title']
            sql['content'] = item['content']
            sql['url'] = item['link']
            sql['add_time'] = str(datetime.date.today())
            sql['is_sent'] =0; #默认还没发给后台
            self.col_content.insert(sql)

            #insert into c_urls
            sql = {}
            sql['url'] = item['link']
            sql['urlhash'] = item['urlhash']
            sql['contenthash'] = item['contenthash']
            sql['crawl_time'] = str(datetime.date.today())
            self.col_ref.insert(sql)


        except :
            print sys.exc_info()
            raise DropItem("重复文章%s" % item)

    #update ArtItem
    def updateArtItem(self, item):
        try :
            #update c_urls
            self.col_ref.update({'urlhash': item['urlhash']}, { '$set': {'contenthash': item['contenthash']}})
            #update c_all_text
            self.col_content.update({'url': item['link']}, { '$set':{'title': item['title'], 'content': item['content']}} )
        except:
            print sys.exc_info();

    #将所有已有的文章urlhash及其内容contenthash的哈希值 置于urlhash
    def setUrlhash(self):
        data = self.col_ref.find({}, {'urlhash':1, 'contenthash':1})
        urlhash = {}
        for row in data :
            urlhash[row['urlhash']] = row['contenthash']
        return urlhash

    def insertUrlItem(self, item):

        #insert into c_urls
        try:
            sql = {}
            sql['url'] = item['url']
            sql['urlhash'] = item['urlhash']
            sql['contenthash'] = item['contenthash']
            sql['crawl_time'] = str(datetime.date.today())
            self.col_ref.insert(sql)
        except :
            print sys.exc_info()

    def  updateUrlItem(self, item):
        try:
            print 'hehhehhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh'
            self.col_ref.update({'urlhash': item['urlhash']}, {'$set' : {'contenthash': item['contenthash']}})
        except:
            print sys.exc_info()
