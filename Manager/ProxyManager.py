# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
-------------------------------------------------
"""
__author__ = 'JHao'

import requests
import random

from Util import EnvUtil
from DB.DbClient import DbClient
from Config.ConfigGetter import config
from Util.LogHandler import LogHandler
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.raw_proxy_queue = 'raw_proxy'
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = 'useful_proxy'
        self.adsl_queue = 'adsl'

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter/getFreeProxy.py
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        for proxyGetter in config.proxy_getter_functions:
            # fetch
            try:
                self.log.info("{func}: fetch proxy start".format(func=proxyGetter))
                for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
                    # 直接存储代理, 不用在代码中排重, hash 结构本身具有排重功能
                    proxy = proxy.strip()
                    if proxy and verifyProxyFormat(proxy):
                        self.log.info('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                        self.db.put(proxy)
                    else:
                        self.log.error('{func}: fetch proxy {proxy} error'.format(func=proxyGetter, proxy=proxy))
            except Exception as e:
                self.log.error("{func}: fetch proxy fail".format(func=proxyGetter))
                continue

    def get(self):
        """
        return a useful proxy
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if item_dict:
            if EnvUtil.PY3:
                return random.choice(list(item_dict.keys()))
            else:
                return random.choice(item_dict.keys())
        return None
        # return self.db.pop()

    def delete(self, proxy):
        """
        delete proxy from pool
        :param proxy:
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        self.db.delete(proxy)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def getNumber(self):
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()
        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}

    def initProxyPool(self):
        """
        第一次启动时调用这个方法
        :return:
        """
        self.deleteAll()
        self.db.changeTable(self.adsl_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.values()) if item_dict else list()
        return item_dict.values() if item_dict else list()

    def deleteAll(self):
        """
        清空代理池
        :param proxy:
        :return:
        """
        # 删除所有
        proxies = self.getAll()
        for proxy in proxies:
            self.delete(proxy)

    def refreshADSL(self, proxy):
        """
        重新拨号
        :param proxy:
        :return:
        """
        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf8')
        ip = proxy.split(':')[0]
        try:
            # 调用接口重新拨号
            refreshApi = "http://{ip}:8000/refresh".format(ip=ip)
            r = requests.get(refreshApi, timeout=5, verify=False)
            if r.status_code == 200:
                print('{proxy} refres done')
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
