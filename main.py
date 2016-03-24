#!/usr/bin/env python
# coding=UTF-8
from house_spider import CityModel
from html_utils import transform

__author__ = 'matrix.lisp@gmail.com'


def init():
    index_url = 'http://bj.ganji.com/xiaoqu'
    create_new = True
    city_model = CityModel(index_url=index_url, create_new=create_new)

    area_select = '//dl[@class="selitem selitem-area lh24 clearfix"]' \
                  '//div[@class=" clearfix"]/a[@rel="nofollow"]'
    subarea_select = '//dl[@class="selitem selitem-area lh24 clearfix"]' \
                     '//div[@class="subarea clearfix"]/a[@rel="nofollow"]'
    city_model.get_basic_data(area_select, subarea_select)
    city_model.save_basic()


def process():
    index_url = 'http://bj.ganji.com/xiaoqu'
    create_new = False
    city_model = CityModel(index_url=index_url, create_new=create_new)
    page_select = '//div[@class="pageBox"]/ul/li/a'
    community_select = '//div[@class="listBox"]/ul/li'
    name_select = './div[@class="list-mod2"]/div[@class="info-title"]/a'
    price_select = './div[@class="list-mod3 xq-price clearfix"]/p/b'
    city_model.get_all_community(page_select, community_select, name_select, price_select)
    city_model.save()


def create_js_data():
    index_url = 'http://bj.ganji.com/xiaoqu'
    create_new = False
    city_model = CityModel(index_url=index_url, create_new=create_new)

    ak = ''
    city = '北京市'
    transform(city_model.community_data, ak, city)


def main():
    # 初始化, 完成基础数据的抓取
    init()

    # 抓取小区信息
    process()

    # 根据小区位置生成热力图所需的js文件
    create_js_data()


if __name__ == '__main__':
    main()
