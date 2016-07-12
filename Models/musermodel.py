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
collection: users mongo 里面的用户模型
structure:

_id 主键
uid  用户id
following_list [] 我所关注的人 同样也是uid的列表，当然有最大数的限制,这里存储的配置信息中人数
				uid 关注的人的id  
				time 关注时间 

following_num 关注的人数
follower_num  粉丝总数
follower_list [] 我的粉丝列表  
			uid  用户id
			time 关注时间
note_list  [] 最近发布到几个帖子，具体帖子数目写在配置文件里
		note_id 帖子id 
		note_title  帖子标题
note_num 帖子总数
group_list [] 团队列表 
		avatar  团队头像 
		group_name 团队名称 
		group_id  团队id
group_num 团队 团队id个数
recent_run:
		distance
		duration 
		id 
interest_list[] 用户兴趣列表
		iid  兴趣id
		iname  兴趣名称

cir_back 

"""
class MUserModel(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.muser 
		self.note_save_num = int(options.note_save_num) #帖子总数
		self.following_save_num = int(options.following_save_num) #用户信息中存储的关注的人的数目 
		self.follower_save_num = int(options.follower_save_num) #   用户信息中存储的粉丝数目
		# self.group_save_sum = options.group_save_sum

	def add_following(self,uid,fuid):
		"""
		添加自己关注的人
		input param: 
				uid:用户id    
				fuid: 关注的人的id
		"""
		uid = int(uid)
		fuid = int(fuid)
		following_info = self.m_c.find_one({'uid':uid,'status':0},{'_id':0,'following_list':1})
		if not following_info or len(following_info['following_list']) < self.following_save_num:
			self.m_c.update({'uid':uid,'status':0},{"$inc":{"following_num":1},"$push":{"following_list":{'uid':fuid,'time':PublicFunc.get_current_stamp()}}},True)
		else:
			following_list = following_info['following_list']
			following_list.insert(0,{'uid':fuid,'time':PublicFunc.get_current_stamp()})
			following_list = following_list[0:self.following_save_num]
			self.m_c.update({'uid':uid,'status':0},{"$inc":{"following_num":1},"$set":{"following_list":following_list}})
		return True


	def cancel_following(self,uid,fuid):
		"""
		删除自己所关注的人
		"""
		uid = int(uid)
		fuid = int(fuid)
		# print fuid
		following_info = self.m_c.find_one({'uid':uid,'status':0},{'_id':0,'following_list':1})
		following_list = following_info['following_list']
		for index,following in enumerate(following_list):
			if following['uid'] == fuid:
				# print 'index:' + str(index)
				del following_list[index]
		self.m_c.update({'uid':uid,'status':0},{"$set":{"following_list":following_list}})
		# db.demo.update({people_id:2, "albums.id":2}, { $set : {"albums.$.name":6 }})
# {"$inc":{"comm_member.$.distance":distance,"comm_member.$.duration":duration}})

	def add_follower(self,uid,fuid):
		"""
		function: 用户id 
		input param: 
				uid:用户id 
				fuid:关注的人的id
		"""
		uid = int(uid)
		fuid = int(fuid)
		follower_info = self.m_c.find_one({"uid":uid,'status':0},{'_id':0,'follower_list':1})
		if not follower_info or len(follower_info) < self.follower_save_num:
			self.m_c.update({'uid':uid,'status':0},{"$inc":{"follower_num":1},"$push":{"follower_list":{'uid':fuid,'time':PublicFunc.get_current_stamp()}}})
		else:
			follower_list = follower_info['follower_list']
			follower_list.insert(0,{'uid':fuid,'time':PublicFunc.get_current_stamp()})
			follower_list = follower_list[0:self.follower_save_num]
			self.m_c.update({'uid':uid,'status':0},{"$inc":{"following_num":1},"$set":{"follower_list":following_list}})
		return True

	def cancel_follower(self,uid,fuid):
		"""
		删除自己的粉丝
		那么uid 不再是fuid的粉丝了

		"""
		uid = int(uid)
		fuid = int(fuid)
		follower_info = self.m_c.find_one({"uid":fuid,'status':0},{'_id':0,'follower_list':1})
		follower_list = follower_info['follower_list']
		for index,follower in enumerate(follower_list):
			if follower['uid'] == uid:
				del follower_list[index]
		self.m_c.update({'uid':fuid,'status':0},{"$set":{"follower_list":follower_list}})
		return True
		


	def add_note(self,uid,note_id,note_title):
		"""将配置个帖子存储到用户信息里面"""
		uid = int(uid)
		note_info = self.m_c.find_one({"uid":uid,'status':0},{'_id':0,'note_list':1})
		if not note_info or len(note_info['note_list']) < self.note_save_num:
			self.m_c.update({'uid':uid,'status':0},{'$inc':{"note_num":1},"$push":{"note_list":{'note_id':note_id,'note_title':note_title}}},True)
		else:
			note_list = note_info['note_list']
			note_list.insert(0,{'note_id':note_id,'note_title':note_title})
			note_list = note_list[0:self.note_save_num]
			self.m_c.update({'uid':uid,'status':0},{"$inc":{"note_num":1},"$set":{"note_list":note_list}})
		return True

	def update_cir_back(self,uid,back_path):
		"""更新用户朋友圈背景图"""
		uid = int(uid)
		self.m_c.update({'uid':uid,'status':0},{"$set":{'cir_back':back_path}})
		return True

	def person_center(self,uid):
		"""
		funtion:  获取用户个人资料  
		author: yinshuai 
		input param:
					uid 
		return: 
				following_num 
				following_list 
						uid 
						time 
				follower_num 
				follower_list 
						uid 
						time 
				note_num
				note_list
						note_id 
						content
				group_list
						group_name
						avatar
						group_id
				interest_list
						iid 
						iname
		"""
		uid = int(uid)
		return self.m_c.find_one({'uid':uid},{'_id':0,'following_list.time':0,'follower_list.time':0})

	def update_cir_back(self,uid,pic_path):
		"""更新用户朋友圈背景图"""
		uid = int(uid)
		return self.m_c.update({"uid":uid},{'$set':{'cir_back':pic_path}},True)




