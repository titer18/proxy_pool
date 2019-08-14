# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

sys.path.append('../')

from Config.ConfigGetter import config
from Manager.ProxyManager import ProxyManager

app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = {
    'get': u'get an usable proxy',
    'get_all': u'get all proxy from proxy pool',
    'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
    'get_status': u'proxy statistics',
    'refresh': u'refresh proxy pool, first get all proxy',
    'pop_all': u'获取所有新代理, 会自动清空, 防止重复',
    'refresh_adsl?proxy=127.0.0.1:8080': u'adsl重新拨号',
    'init_proxy_pool': u'初始化代理池, 适用于异常清空了代理池, 然而没有调用adsl重新拨号, 代理池就会一直是空的, 建议首次启动程序的时候调用一次'
}


@app.route('/')
def index():
    return api_list


@app.route('/get/')
def get():
    proxy = ProxyManager().get()
    return proxy if proxy else 'no proxy!'


# @app.route('/refresh/')
# def refresh():
#     # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
#     # ProxyManager().refresh()
#     pass
#     return 'success'


@app.route('/get_all/')
def getAll():
    proxies = ProxyManager().getAll()
    return proxies


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    ProxyManager().delete(proxy)
    return 'success'


@app.route('/get_status/')
def getStatus():
    status = ProxyManager().getNumber()
    return status


@app.route('/init_proxy_pool/')
def initProxyPool():
    proxies = ProxyManager().initProxyPool()
    return proxies

@app.route('/pop_all/')
def popAll():
    proxies = ProxyManager().getAll()
    ProxyManager().deleteAll()
    return proxies

@app.route('/refresh_adsl/', methods=['GET'])
def refreshADSL():
    proxy = request.args.get('proxy')
    ProxyManager().refreshADSL(proxy)
    return 'success'

def run():
    app.run(host=config.host_ip, port=config.host_port)


if __name__ == '__main__':
    run()
