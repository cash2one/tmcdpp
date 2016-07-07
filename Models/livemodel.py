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
from Func.publicfunc import PublicFunc
from tagmodel import TagModel
from usersmodel import UsersModel

class LiveModel(DbBase):
    def __init__(self):
    	DbBase.__init__(self)
    	self.table = 'fs_lives'

    def get_live_list(self,gid):
    	"""根据赛事id 获取赛事实况列表"""
    	live_list =  self.find_data(['*'],order='time desc',gid=gid,status=0)
    	for index,live in enumerate(live_list):
    		live_list[index]['pic'] = options.ipnet + live['pic']
    		live_list[index]['time'] = PublicFunc.stamp_to_YmdHM(live['time'])
        return live_list
        
    @classmethod
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = LiveModel()
    	return cls.model_instance

