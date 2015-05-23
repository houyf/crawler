#!/usr/bin/env python
# coding=utf-8

from scrapy import log

"""避免被ban策略之一：使用useragent池。

使用注意：需在settings.py中进行相应的设置。
"""

import random
import utips.settings as settings
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware

class RotateUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        ua = random.choice(settings.USER_AGENT_LIST)
        if ua:
            log.msg('Current UserAgent: '+ua, level='INFO')
            request.headers.setdefault('User-Agent', ua)

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.HTTP_PROXY

