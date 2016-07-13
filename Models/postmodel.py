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
collection: postmodel  朋友圈说说模型  
structure:

_id 主键
uid  用户id 发布朋友圈的人
love_num 点赞总数
com_num 评论总数
pic_list
		[] 图片列表 存储图片url相对地址 max 9 
love_list 
		[]喜欢列表  存储用户 {'uid':''}
comm_list 
		[] 评论列表只存储一页数据
		uid 用户id  
		time 评论时间 
		content 评论内容 
pic_num 图片数
content 说说内容
time 发布时间
status 帖子状态

"""
class PostModel(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.post
		self.post_per_page = int(options.post_per_page)
		

	def get_post_list(self,uid,page):
		"""
		function: 获取朋友圈说说列表
		"""
		pass

	def get_post_info(self,post_id):
		"""
		function: 获取说说详情
		"""
		post_info = self.m_c.find_one({'_id':ObjectId(post_id),'status':0})
		return post_info

	def release_post(self,uid,pic_list,content,address,pic_num,longitude,latitude):
		"""
		function: 发布说说
		input param: 
				uid 用户id  
				pic_list  朋友圈说说图片列表
				content 朋友圈内容
				address 发布地
				pic_num
		return param: success or except 
		"""
		uid = int(uid)
		post_id = self.m_c.insert({'status':0,'uid':uid,'love_list':[],'pic_num':pic_num,'pic_list':pic_list,'content':content,'comm_list':[],
									'love_num':0,'com_num':0,'address':address,'longitude':longitude,'latitude':latitude,'time':int(time.time())})
		return str(post_id)

	def comm_num_oper(self,post_id,num):
		"""修改说说评论次数"""
		self.m_c.update({'_id':ObjectId(post_id)},{"$inc":{'com_num':num}})
		return True

	def love_num_oper(self,post_id,num):#NO USE now 
		self.m_c.update({'_id':ObjectId(post_id)},{"$inc":{'love_num':num}})
		return True

	def love_oper(self,uid,post_id):
		"""对喜欢的说说的操作，这里既包含了增加了喜欢的条数，还包含修改喜欢用户数组"""
		uid = int(uid)
		love_user_len = int(options.post_love_len)
		love_user_list = self.m_c.find_one({"_id":ObjectId(post_id)},{'love_list':1,'_id':0})['love_list']
		love_user_list.insert(0,{'uid':uid})
		love_user_list = love_user_list[0:love_user_len]
		self.m_c.update({'_id':ObjectId(post_id)},{"$inc":{'love_num':1},"$set":{"love_list":love_user_list}})
		return True


	def update_comm_list(self,uid,post_id,comm_content):
		"""
		function : 更新post集合中的第一页评论
		"""
		uid = int(uid)
		comm_list = self.m_c.find_one({"_id":ObjectId(post_id)},{'comm_list':1,'_id':0})['comm_list']
		comm_list.insert(0,{'uid':uid,'comm_content':comm_content,'time':int(time.time())})
		comm_per_page  = int(options.post_comm_per_page)
		comm_list = comm_list[0:comm_per_page]
		self.m_c.update({'_id':ObjectId(post_id)},{"$set":{'comm_list':comm_list}})
		return True 

	def get_post_list(self,page):
		"""
		function: 获取说说列表 
		"""
		page = int(page)
		post_per_page = int(options.post_per_page)
		post_list = list(self.m_c.find({'status':0},{'comm_list':0,'love_list':0,'latitude':0,'longitude':0}).sort([('time',-1)]).skip(page*post_per_page).limit(post_per_page))
		return post_list

	def get_post_num(self,post_id):
		"""判断说说是否存在"""
		return self.m_c.find({"_id":ObjectId(post_id)},{'status':0}).count()

	def recommend_user(self):
		"""
		推荐两个用户 有帖子的用户哦亲
		"""
		init_num = 0
		recommend_user_info = []
		while True:
			post_list = self.m_c.find({'status':0},{'uid':1,'pic_num':1,'pic_list':1}).skip(init_num).limit(2)
			init_num += 2
			if len(recommend_user_info) >= 2 :break
			for post in post_list:
				if len(recommend_user_info) >= 2 :break
				if post['pic_num'] >= 3:
					post['pic_list'] = post['pic_list'][:3]
					recommend_user_info.append(post)
		return recommend_user_info


	def get_user_post(self,uid,page):
		"""获取用户朋友圈"""
		page = int(page)
		uid = int(uid)
		post_per_page = self.post_per_page
		post_list = list(self.m_c.find({'status':0,'uid':uid},{'comm_list':0,'latitude':0,'longitude':0,'love_list':0,'pic_list':{"$slice":[0,3]}}).sort([('time',-1)]).skip(page*post_per_page).limit(post_per_page)) 
		return post_list




