# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArtItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    contenthash = scrapy.Field()
    link = scrapy.Field()
    urlhash = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()
    pass
    # def __str__(self):
        # print '%s为文章' % self.link

#无法匹配的文章
class RubbishItem(scrapy.Item):
    url = scrapy.Field()
    urlhash = scrapy.Field()
    contenthash = scrapy.Field()

class UrlItem(scrapy.Item):
    url = scrapy.Field()
    urlhash = scrapy.Field()
    contenthash = scrapy.Field()
    pass

#图片
class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    pass

