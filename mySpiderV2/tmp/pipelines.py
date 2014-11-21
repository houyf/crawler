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
                print '%s 列表页发生更改' % item['url']
                self.updateUrlItem(item)
            else :
                print '%s 是未收录的列表页'% item['url']
                self.insertUrlItem(item)

        #if is the article
        else :
            #对item的title和content 格式化处理
            item['title'] = item['title'].replace('"', '\"')
            item['title'] = item['title'].replace("'", "\'")
            item['content'] = item['content'].replace('"', '\"')
            item['content'] = item['content'].replace("'", "\'")
            self.insertArtItem(item)

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
            self.col_ref.update({'urlhash': item['urlhash']}, {'$set' : {'contenthash': item['contenthash']}})
        except:
            print sys.exc_info()
