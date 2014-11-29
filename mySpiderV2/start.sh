#!/bin/bash
# /home/houyf/shell/test.sh

PATH=$PATH:/usr/local/bin
export PATH
cd /home/houyf/crawler/mySpiderV2/
scrapy crawl MySpider
