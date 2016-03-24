#!/usr/bin/env python
# coding=UTF-8
from house_spider import CityModel
from html_utils import transform

__author__ = 'matrix'


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


def test():
    index_url = 'http://bj.ganji.com/xiaoqu'
    create_new = False
    city_model = CityModel(index_url=index_url, create_new=create_new)

    ak = 'Gngv8fFQ63xtivWZaZzGOGM8'
    city = '北京市'
    transform(city_model.community_data, ak, city)

    # for area in city_model.area_data.keys():
    #     temp_data = city_model.subarea_data[area]
    #     print area
    #     for subarea, url in temp_data.iteritems():
    #         print '\t', subarea, url

    # for name, price in city_model.community_data.iteritems():
    #     print name, type(name), price


if __name__ == '__main__':
    # init()
    # process()
    test()
