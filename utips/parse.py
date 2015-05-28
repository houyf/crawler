#!/usr/bin/env python
# coding=utf-8
import socket
import logging
import threading
import time

class Item(dict):
    pass


def singleton(cls):
    """
    单例针对每个进程而言
    """
    instances = {}
    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def singletonThreadSave(cls):
    """
    单例针对每个线程而言
    """
    instances = {}
    def _singleton(*args, **kw):
        import threading 
        current_thread = threading.current_thread();
        if cls not in instances:
            instances[cls]  = {}
        if current_thread not in instances[cls]:
            instances[cls][current_thread] = cls(*args, **kw)
        return instances[cls][current_thread]
    return _singleton


def Lock(func):
    """
    给一个函数加锁
    """
    import threading
    lock = threading.Lock() 
    def wrapper(*args, **kw):
        lock.acquire()
        try:
            func(*args, **kw)
        finally:
            lock.release()
    return wrapper 


@singleton
class IpPool(object):
    def __init__(self):
        self._ipPool = self.getIpSaved()

    def getIpSaved(self):
        conn = DbConnection().conn
        ipPool = conn['proxy'].find({}, {'ip':1})
        return map(lambda i: i['ip'], ipPool) 

    def getIpPool(self):
        return self._ipPool;
    
    @Lock
    def insert(self, ip): 
        if ip not in self._ipPool:
            self._ipPool.append(ip)
    

@singletonThreadSave
class DbConnection(object):
    """
        hostname = '127.0.0.1'
        port = 27017
        database = 'utipsV2'
        conn1 = DbConnection(hostname, port, database).conn
        print id(conn1)
        conn2 = DbConnection(hostname, port, database).conn
        print id(conn2)
    """
    conn = None
    def __init__(self):
        hostname = '127.0.0.1'
        port = 27017
        database = 'utipsV2'
        import pymongo
        self.__class__.conn = pymongo.Connection(hostname, port)
        self.__class__.conn = self.__class__.conn[database]
        

def fetchContent():
    conn = DbConnection().conn
    page = conn['youdaili'].find_and_modify({'isHandled':False}, {'$set':{'isHandled':True}})
    return  page if page is None else page.get('content', None) 


def parse(content):
    try:
        content = content.replace('<br>', '')
        lines = content.split('\r\n')
        lines = map(lambda x: x.strip(), lines)
        def parse_item(line):
            try:
                ip, rest = line.split(':')
                port, rest = rest.split('@')
                protocol, info = rest.split('#')
                item = Item()
                item['ip'] = ip
                item['port'] = int(port)
                item['protocol'] = protocol
                item['info'] = info
            except:
                return None
            else:
                return item
        lines = map(parse_item, lines)
        return filter(lambda x: x is not None, lines)
    except :
        logging.error('content is fail to parse to parse')
        return []


def saveItem(item):
    conn = DbConnection().conn
    collection_name = 'proxy'
    if collection_name not in conn.collection_names():
        conn.create_collection(collection_name)
    conn[collection_name].insert(item)
    

def proxyCost(item, timeout = 3, testNum = 3):
    """
    测试代理是否可用
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.settimeout(timeout) 
    try:
        cost  = []
        for i in xrange(0, testNum): 
            start = time.time()
            s.connect((item['ip'], item['port']))
            cost.apend(time.time() - start)
            s.close()
        logging.info('{ip}:{port} is useful'.format(ip=item['ip'], port=item['port']))
        return sum(cost/len(cost))  
    except socket.error:
        logging.info('{ip}:{port} is useless'.format(ip=item['ip'], port=item['port']))
        return 10 


def work():
    """
    分析篇文章的代理ip可用性
    """
    content = fetchContent()
    if content is None:
        logging.info('worker%s exit normally.'% threading.current_thread())
        exit(0)
    # while content:
    items = parse(content)
    ipPool = IpPool();
    for i in items:
        if i['ip'] not in ipPool.getIpPool() and proxyCost(i) < 2:
            ipPool.insert(i['ip'])
            saveItem(i)
        # content = fetchContent()

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s  %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S'
    )
    threads = []
    n = 150
    for i in xrange(0, n):
        t = threading.Thread(target=work, name='worker{id}'.format(id=threading.current_thread()))
        t.start() 
        logging.debug('worker{id} is working ...'.format(id=threading.current_thread()))
        threads.append(t)
    for t in threads:
        t.join()
    