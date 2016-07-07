#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import sys
import copy
import operator
import socket
from tornado.options import define, options
import json
import config
from  pdatabase import DbBase
class TagModel(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_tag'

    @classmethod
    def get_instance(cls):
        if not cls.model_instance: cls.model_instance = TagModel()
        return cls.model_instance

    def get_all_tag(self):
        if not self.cache.exists('tag_all'):
    	    ad_list = self.find_data(['*'])
    	    for index,value in enumerate(ad_list):
    	    	ad_list[index]['pic'] =  options.ipnet + '/Uploads/TagPic/' +  value['pic']
    	    print ad_list
            self.cache.set('tag_all',ad_list)
        return eval(self.cache.get('tag_all'))


    def cache_tag_name(self,tag_id):
        tag_id = str(tag_id)
        if not self.cache.exists('tag:id:' + tag_id + ':name'):
            tag_name = self.find_data(['name'],get_some=False,id=tag_id)['name']
            self.cache.set('tag:id:' + tag_id + ':name',tag_name)

    def get_tag_name(self,tag_id):
        self.cache_tag_name(tag_id)
        return self.cache.get('tag:id:' + str(tag_id) + ':name')
