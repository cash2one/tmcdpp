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
class AdModel(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_ad'

    @classmethod
    def get_instance(cls):
        if not cls.model_instance: cls.model_instance = AdModel()
        return cls.model_instance

    def get_all_ad(self):
        if not self.cache.exists('ad_pic'):
    	    ad_list = self.find_data(['*'])
    	    for index,value in enumerate(ad_list):
                ad_list[index]['pic'] = options.ipnet + value['pic']
            self.cache.set('ad_pic',ad_list)
        return eval(self.cache.get('ad_pic'))

    	

