#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import re
import redis
import time
import tornado.options
import unicodedata
import sys
import random
import hashlib
from random import sample
import copy
import operator
import socket
from tornado.options import define, options
import json
import config
from pmongo import MongoBase
from Func.publicfunc import PublicFunc
from usersmodel import UsersModel

class InteractModel(MongoBase):
    """一个简单到模型，关于跑团和赛事互动的"""
    def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.interact
    
    @classmethod
    def get_instance(cls):
    	if not cls.model_instance: 
    		cls.model_instance = InteractModel()
    	return cls.model_instance

    def add_interact(self,uid,content,comm_id):
    	"""用户提交互动信息，uid可以为0 ，为0的时候表示游客"""
    	uid = int(uid)
        c_t = PublicFunc.get_current_stamp()
        data_write = {'uid':uid,'content':content,'comm_id':comm_id,'time':c_t}
        return self.m_c.insert(data_write)

    def get_interact(self,comm_id,page):
    	"""直接根据团队id获取这个互动  这块还是先查到这条数据的id 再查找多条数据"""
    	# return [rows for rows in self.m_c.find({search_key:int(id)})]
    	page = int(page)
    	per_page = 10 
    	interact_info = self.m_c.find({'comm_id':comm_id},{'content':1,'time':1,'_id':0,'uid':1}).skip(per_page*page).limit(per_page).sort([('time',-1)])
    	interact_list = [] 
    	current_time = PublicFunc.get_current_stamp()
    	index = page * per_page
    	for info in interact_info:
    		index += 1 
    		info['time'] = PublicFunc.time_format_span(info['time'],current_time)
    		info['index'] = index
    		if not info['uid']:
    			info['avatar'] = 'http://101.200.214.68/Uploads/head.png'
    			info['nickname'] = '游客'
    		else:
    			user_info = UsersModel.get_instance().get_import_user_info(info['uid'],['avatar','username'])
    			info['avatar'] = user_info['avatar']
    			info['nickname'] = user_info['username']
    		del info['uid']
    		interact_list.append(info)
    	return interact_list










