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
collection: follow 我所关注的人的集合
structure:


_id 主键
uid  用户id
fuid 关注的人的id 
time 关注时间
status 用户id 
"""
class FollowModel(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.follow
		self.following_per_page = int(options.following_per_page)
		self.usersmodel = UsersModel()


	def following_man(self,uid,fuid):
		"""
		function: 关注他人
		input param: 
				uid 关注时间
				fuid  关注的人的id 
		"""
		uid = int(uid)
		fuid = int(fuid)
		count = self.m_c.find({'uid':uid,'fuid':fuid,'status':0}).count()
		if count: return 'has_following' 
		else:
			self.m_c.insert({'uid':uid,'fuid':fuid,'status':0,'time':PublicFunc.get_current_stamp()})
			return 'following'


	def get_following_list(self,uid,page):
		"""
		function: 获取用户关注的人的列表
		input param:
				uid 用户id  
				page 分页
		"""
		uid = int(uid)
		page = int(page)
		following_list = self.m_c.find({'uid':uid,'status':0},{'_id':0,'status':0,'uid':0}).sort([('time',-1)]).skip(self.following_per_page*page).limit(self.following_per_page)
		return list(following_list)

	def get_follower_list(self,uid,page):
		"""
		function: 获取用户粉丝列表
		input param:
				uid 用户id  
				page 分页
		"""
		uid = int(uid)
		page = int(page)
		follower_list = self.m_c.find({'fuid':uid,'status':0},{'_id':0,'uid':1,'time':1}).sort([('time',-1)]).skip(self.following_per_page*page).limit(self.following_per_page)
		return list(follower_list)

	




