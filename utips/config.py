#!/usr/bin/env python
# coding=utf-8

class ConfigContainer(object):
    _website_config = None
    def __init__(self, website_config):
        self.__class__. _website_config = website_config

    @classmethod 
    def getWebsiteConfig(cls, key):
        return cls._website_config.get(key, None)
