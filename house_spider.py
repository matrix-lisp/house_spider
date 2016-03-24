#!/usr/bin/env python
# coding=UTF-8
import os
import time
import cPickle as pickle

from html_utils import get_doc
from html_utils import get_link_data
from html_utils import get_community_data

__author__ = 'matrix.lisp@gmail.com'


class CityModel(object):
    DEFAULT_DATA_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data/model.dat")
    DEFAULT_BASIC_DATA_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data/basic.dat")

    def __init__(self, index_url, file_path=None, basic_file_path=None, create_new=False):
        """
        城市模型, 封装一个城市的基本信息
        :param index_url: 城市主页面
        :param file_path:
        :param basic_file_path
        :param create_new:
        :return:
        """
        self.file_path = file_path if file_path else self.DEFAULT_DATA_PATH
        self.basic_file_path = basic_file_path if basic_file_path else self.DEFAULT_BASIC_DATA_PATH
        self.create_new = create_new
        if self.create_new:
            self.index_url = index_url
            self.domain = '/'.join(index_url.split('/')[:3])
            # 城市的所有区域
            self.area_data = {}
            # 城市的所有子区域, 以区域名为key, 以该区域下的子区域列表为value
            self.subarea_data = {}
            # 城市的所有小区, 以子区域为key, 以该区域下的小区列表为value
            self.community_data = {}
        else:
            if os.path.exists(self.file_path):
                self.index_url, self.area_data, self.subarea_data, self.community_data = self.load(self.file_path)
            elif os.path.exists(self.basic_file_path):
                self.index_url, self.area_data, self.subarea_data = self.load(self.basic_file_path)
                self.community_data = {}
            self.domain = '/'.join(index_url.split('/')[:3])

    def load(self, file_path=None):
        """
        加载已爬取城市的房屋数据
        :param file_path:
        """
        file_path = file_path if file_path else self.DEFAULT_DATA_PATH
        if not os.path.exists(file_path):
            with open(file_path, 'a'):
                os.utime(file_path, None)
        with open(file_path, 'rb') as f:
            try:
                return pickle.load(f)
            except pickle.UnpicklingError:
                return '', {}, {}, {}

    def load_basic(self, basic_file_path=None):
        """
        加载已爬取城市的基础数据
        :param basic_file_path:
        """
        basic_file_path = basic_file_path if basic_file_path else self.DEFAULT_BASIC_DATA_PATH
        if not os.path.exists(basic_file_path):
            with open(basic_file_path, 'a'):
                os.utime(basic_file_path, None)
        with open(basic_file_path, 'rb') as f:
            try:
                return pickle.load(f)
            except pickle.UnpicklingError:
                return '', {}, {}

    def save(self):
        """
        保存已爬取城市的房屋数据
        """
        with open(self.file_path, 'wb') as f:
            pickle.dump((self.index_url, self.area_data, self.subarea_data, self.community_data), f, -1)

    def save_basic(self):
        """
        保存已爬取城市的基础数据
        """
        with open(self.basic_file_path, 'wb') as f:
            pickle.dump((self.index_url, self.area_data, self.subarea_data), f, -1)

    def _get_all_area(self, select, url=None):
        """
        抓取区域信息
        :param select:
        :param url:
        :return:
        """
        if url is None:
            url = self.index_url
        doc = get_doc(url)
        self.area_data = get_link_data(select, doc=doc)

    def _get_all_subarea(self, select):
        """
        抓取子区域信息
        :param select:
        :return:
        """
        for name, url in self.area_data.iteritems():
            if url.startswith('/'):
                url = self.domain + url
            print name, url
            doc = get_doc(url)
            temp_data = get_link_data(select, doc=doc)
            self.subarea_data[name] = temp_data

    def get_basic_data(self, area_select, sub_area_select):
        """
        根据指定的规则抓取某个城市下所有的区域、子区域作为基础数据
        :param area_select: 区域选择器
        :param sub_area_select: 子区域选择器
        :return:
        """
        # 1. 抓取起始页并解析区域信息
        self._get_all_area(area_select)

        # 2. 遍历每个区域并解析隶属该区域的子区域信息
        self._get_all_subarea(sub_area_select)

    def get_all_community(self, page_select, community_select, name_select, price_select):
        """
        抓取小区信息
        :param page_select: 页面选择器, 用于翻页
        :param community_select: 小区选择器, 用于匹配当前页面内的所有小区
        :param name_select: 小区名称选择器
        :param price_select: 小区均价选择器
        :return:
        """
        for area in self.area_data.keys():
            # if area != '密云':
            #     continue
            print area
            temp_data = self.subarea_data[area]
            for subarea, url in temp_data.iteritems():
                # if subarea != '不老屯':
                #     continue
                html_file = 'data/html/%s/%s/%s.html' % (area, subarea, url.split('/')[2])
                if url.startswith('/'):
                    url = self.domain + url

                doc = get_doc(url, file_name=html_file)
                print '\n', subarea, url,
                community_data = get_community_data(doc, community_select, name_select, price_select)

                page_data = get_link_data(page_select, doc=doc)
                for page_num, page_url in page_data.iteritems():
                    if not page_num.isdigit():
                        continue
                    if page_url is None:
                        continue
                    if page_url == url:
                        continue

                    html_file = 'data/html/%s/%s/%s.html' % (area, subarea, page_url.split('/')[2])
                    if page_url.startswith('/'):
                        page_url = self.domain + page_url

                    print page_num, page_url,
                    time.sleep(1)

                    doc = get_doc(page_url, file_name=html_file)
                    community_data = dict(get_community_data(doc, community_select, name_select, price_select),
                                          **community_data)

                self.community_data = dict(self.community_data, **community_data)
