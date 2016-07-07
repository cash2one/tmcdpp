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
from bson.objectid import ObjectId


"""
collection: postlove  说说喜爱模型  
structure:

_id 主键
uid  用户id 
post_id 说说id
time 点赞时间
status 状态

"""
class PostLove(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.postlove

	def send_love(self,uid,post_id):
		"""
		function: 发送对说说的爱,首先查看用户是否已经发送过爱了
		"""
		uid = int(uid)
		count = self.m_c.find({'post_id':post_id,'uid':uid}).count()
		if count : return 'have_send_love'
		else:
			self.m_c.insert({'uid':uid,'post_id':post_id,'status':0,'time':int(time.time())})
			return 'send_love'

	def judge_post_love(self,uid,post_id):
		"""看看自己有没有对某个说说表示爱意"""
		uid = int(uid)
		post_id = str(post_id)
		count = self.m_c.find({'post_id':post_id,'uid':uid}).count()
		return True if count else False 

	def get_lover_list(self,post_id,page):
		"""
		function: 获取说说的喜欢用户列表     
		input param: 
				post_id 说说id
				page 分页
		"""
		page = int(page)
		lover_per_page = int(options.post_lover_per_page)
		lover_cur = self.m_c.find({"post_id":post_id}).sort([('time',-1)]).skip(page*lover_per_page).limit(page)
		lover_list = list(lover_cur)
		return lover_list
