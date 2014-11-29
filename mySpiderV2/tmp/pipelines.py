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
import MySQLdb
from twisted.enterprise import adbapi
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy import Request
import hashlib

#连接数据库
class MySQLStorePipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            db = 'utipsV2',
            user = 'houyf',
            passwd = 'Beyond',
            cursorclass = MySQLdb.cursors.DictCursor,
            charset = 'utf8',
            use_unicode = False
        )

        self.urlhash = {}
        self.dbpool.runInteraction(self.setUrlhash)

    #pipeline默认调用
    def process_item(self, item, spider):
        # if not the article
        if (isinstance(item, UrlItem)):
            # update or insert the UrlItem
            if(item['urlhash']  in self.urlhash):
                print '%s 列表页发生更改' % item['url']
                self.dbpool.runInteraction(self.updateUrlItem, item)
            else :
                print '%s 是未收录的列表页'% item['url']
                self.dbpool.runInteraction(self.insertUrlItem, item)

        #if is the article
        else :
            #对item的title和content 格式化处理
            item['title'] = item['title'].replace('"', '\"')
            item['title'] = item['title'].replace("'", "\'")
            item['content'] = item['content'].replace('"', '\"')
            item['content'] = item['content'].replace("'", "\'")
            self.dbpool.runInteraction(self.insertArtItem, item)

        return item

    def insertArtItem(self, tx, item):
        try :
            #插入记录到c_all_text
            tx.execute('insert into `c_all_text`(`title`, `content`, `url`, `add_time`) \
            values (%s, %s, %s, %s)', (item['title'], item['content'], item['link'], str(datetime.date.today())))
            #插入记录到c_urls
            sql = 'insert into c_urls(`url`, `urlhash`, `contenthash`, `crawl_time`)' \
            + 'values("%s", "%s", "%s", "%s")' % (item['link'], item['urlhash'], item['contenthash'], str(datetime.date.today()) )
            tx.execute(sql)

        except :
            print sys.exc_info()
            raise DropItem("重复文章%s" % item)

    #将所有已有的文章urlhash及其内容contenthash的哈希值 置于urlhash
    def setUrlhash(self, tx):
        sql = 'select `urlhash`, `contenthash`  from c_urls'
        tx.execute(sql)
        data = tx.fetchall()
        for row in data :
            self.urlhash[row['urlhash']] = row['contenthash']

    def insertUrlItem(self, tx, item):
        sql = 'insert into c_urls(`url`, `urlhash`, `contenthash`, `crawl_time`)' \
        + 'values("%s", "%s", "%s", "%s")' % (item['url'], item['urlhash'], item['contenthash'], str(datetime.date.today()) )
        tx.execute(sql)

    def  updateUrlItem(self, tx, item):
        sql = 'update c_urls  ' + ' set `contenthash` = "%s" where `urlhash` = "%s" ' \
        % ( item['contenthash'], item['urlhash'])
        tx.execute(sql)


#自定义图片处理管道
class  ImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield Request(image_url)

    def item_completed(self, results, item, info):
        print results
        image_paths = [hashlib.new('md5', x['url']).hexdigest() for ok, x in results if ok]

        if not image_paths:
            raise DropItem('该文章没有图片')
        item['image_paths'] = image_paths
        return item

    #改写文件路径,用md5
    def file_path(self, request, response=None, info=None):
        # return  request.url.split('/')[-1]
        return  hashlib.new('md5', request.url).hexdigest() + '.'  + request.url.split('.')[-1]




