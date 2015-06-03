#!/usr/bin/env python
# -*- coding: utf8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self): 
        """
        GET request 
        args : id  limit(default unlimited)
        return json of msgs
        for each item in msgs has the structure like:
            title
            content
            crawl_time
        """
        def msgToPub(id, limit = None):
            """
            func:
                get msgs unsent from mongodb  according to id and limit
            args :
                id: id of the site in database
                limit: limit max msgs (default unlimited)
            return:
                a list of msgs, each msg is a dict has keys like:
                title, content, crawl_time
            """
            id = int(id)
            limit = int(limit)
            import pymongo 
            conn = pymongo.Connection('127.0.0.1', 27017)
            db = conn['utipsV2']
            table = db['website'].find_one({'id':id},{'TABLE':1})
            if not table:
                return []
            table = table['TABLE']
            if limit is not None:
                cursor = db[table].find({'isSend': {'$exists':False}}).limit(limit)
            else:
                cursor = db[table].find({'isSend': {'$exists':False}})
            msgs = []
            for i in cursor:
                db[table].update({'_id': i['_id']}, {'$set': {'isSend':True}})
                item = {
                    'title': i['title'], 
                    'content': i['content'], 
                    'crawl_time': i['crawl_time']
                }
                msgs.append(item)
            return msgs

        id = self.get_argument('id')
        limit = self.get_argument('limit', None)
        msgs = msgToPub(id, limit)
        """
            test json
        >>> import json 
        >>> data = {'3':[{'1': 1}, 2]}
        >> print json.dumps(data)
        """
        from json import dumps
        self.write(dumps(msgs))


if __name__ == "__main__":
    application = tornado.web.Application([(r"/", MainHandler),], debug=True)
    options.parse_command_line()
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
