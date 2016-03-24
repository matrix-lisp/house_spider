#!/usr/bin/env python
# coding=UTF-8
import os
import sys
import json
import gzip
import urllib2
import cStringIO

from lxml import etree

__author__ = 'matrix.lisp@gmail.com'

reload(sys)
sys.setdefaultencoding('UTF-8')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Connection': 'keep-alive'
           }


def get_html_content(url):
    """
    使用urllib2库实现网页抓取, 特别处理了网页内容经过压缩的情况
    :param url:
    :return:
    """
    message = 'OK'
    html = None
    try:
        req = urllib2.Request(url, headers=headers)
        www = urllib2.urlopen(req, timeout=10)
        html = www.read()
        if html[:6] == '\x1f\x8b\x08\x00\x00\x00':
            html = gzip.GzipFile(fileobj=cStringIO.StringIO(html)).read()
        www.close()
    except Exception, e:
        if isinstance(e, urllib2.HTTPError):
            message = 'http error: %s' % (e.__str__())
        elif isinstance(e, urllib2.URLError):
            message = 'socket error: %s' % (e.__str__())
        else:
            message = 'misc error: %s' % (e.__str__())
    return message, html


def get_doc(url, max_num=3, file_name=None):
    """
    根据url或文件名加载doc
    :param url:
    :param max_num:
    :param file_name:
    :return:
    """
    if file_name and os.path.exists(file_name):
        print '\t\tdownload'
        html = file(file_name).read()
        doc = etree.HTML(html)
        return doc

    num = 0
    message = ''
    html = None
    while message != 'OK' and num < max_num:
        message, html = get_html_content(url)
        num += 1
    if html is None:
        print message
        return None

    doc = etree.HTML(html)

    if file_name:
        file_path = '/'.join(file_name.split('/')[:-1])
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file_name, 'w') as html_file:
            html_file.write(html)

    return doc


def get_link_data(select, url=None, doc=None):
    """
    使用指定的选择器在文档中解析某一类链接
    :param select:
    :param url:
    :param doc:
    :return:
    """
    if doc is None:
        doc = get_doc(url)
    data = {}
    item_list = doc.xpath(select)
    for item in item_list:
        item_host = item.get('href')
        item_name = item.xpath("string()")
        data[item_name] = item_host
    return data


def get_community_data(doc, community_select, name_select, price_select):
    """
    匹配小区信息
    :param doc:
    :param community_select:
    :param name_select:
    :param price_select:
    :return:
    """
    community_list = doc.xpath(community_select)
    data = {}
    for community in community_list:
        try:
            name = community.xpath(name_select)[0].xpath('string()')
            price = community.xpath(price_select)[0].xpath('string()')
            data[name] = price
            print '\t', name, price
        except IndexError:
            continue
    return data


def get_coordinate(address, ak, city):
    """
    使用百度API接口进行地址转换
    :param address:
    :param ak:
    :param city:
    :return:
    {"status": 0,
     "result": {
         "location": {
             "lng": 116.34213332629,
             "lat": 39.997261285991
         },
         "precise": 0,
         "confidence": 60,
         "level": "地产小区"
     }}
    """
    api_url = 'http://api.map.baidu.com/geocoder/v2/?ak=%s&output=json&city=%s&address=%s' % (ak, city, address)
    message, result = get_html_content(api_url)
    if message != 'OK':
        print message
        return None
    return json.loads(result)


def transform(community_data, ak, city):
    """
    根据小区名称获取地理位置信息并构建热力图所需的数据格式
    :param community_data:
    :param ak
    :param city
    :return:
    """
    points = []
    for name, price in community_data.iteritems():
        obj = get_coordinate(name, ak, city)
        if obj is None:
            continue
        if obj['status'] != 0:
            continue
        d = obj['result']['location']
        d['price'] = round(int(price)/1000.0, 2)
        points.append(d)
    with open('doc/js/points.js', 'w') as js_file:
        js_file.write('var points = ' + json.dumps(points) + ';')
