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
collection: note  帖子模型
structure:


_id 主键
uid  用户id
title 帖子标题
content 帖子内容
time 发布时间
special  是否加精 1:yes 0:no 
up  置顶时间， 如果为0表示没有置顶
look_num  观察数 
com_num 评论数 
status 帖子状态

"""


class NoteModel(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.note
	@classmethod
	def get_instance(cls):	    
		if not cls.model_instance: cls.model_instance = NoteModel()
		return cls.model_instance


	def release_note(self,uid,title,content):
		""" 发布帖子"""
		uid = int(uid)
		note_id = self.m_c.insert({'uid':uid,'title':title,'content':content,'time':PublicFunc.get_current_stamp(),'special':0,'up':0,'look_num':0,'com_num':0,'status':0})
		return str(note_id)

	def get_note_list(self,page):
		"""
		function:获取帖子列表
             置顶的排在前面，第二顺序为发布时间，时间越晚越靠前
		"""
		note_per_page = int(options.note_per_page)
		page = int(page)
		note_list = list(self.m_c.find({'status':0},{'content':0,'status':0}).sort([('up',-1),('time',-1)]).skip(note_per_page*page).limit(note_per_page))
		print note_list
		current_time = PublicFunc.get_current_stamp()
		for note in note_list:
			note['time'] = PublicFunc.time_format_span(note['time'],current_time)
			user_info = UsersModel.get_instance().get_import_user_info(note['uid'],['nickname','avatar'])
			note['avatar'] = user_info['avatar'] 
			note['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
			note['is_up'] = 1 if int(note['up']) else 0 
			del note['up']
			note['note_id'] = str(note['_id'])
			del note['_id']
		return note_list

	def get_note_info(self,note_id):
		"""获取帖子信息"""
		note_info = self.m_c.find_one({"_id":ObjectId(note_id),'status':0})
		note_info['time'] = PublicFunc.time_format_span(note_info['time'],PublicFunc.get_current_stamp())
		note_info['note_id'] = str(note_info['_id'])
		note_info['is_up'] = 1 if note_info['up'] else 0 
		del note_info['_id']
		del note_info['status']
		return note_info

	def get_note_comm_num(self,note_id):
		"""获取帖子评论总数"""
		comm_num = self.m_c.find_one({"_id":ObjectId(note_id)},{'_id':0,'com_num':1})['com_num']
		return comm_num

	def update_note_comm_num(self,note_id,num):
		"""
		function: 更新帖子评论数目字段    
		input param: 
		        note_id: 帖子id 
		        num: 变化值
		return param: True or except 
		"""
		self.m_c.update({'_id':ObjectId(note_id)},{'$inc':{'com_num':num}})

	def get_note_num(self,note_id):
		"""获取帖子数目"""
		result = self.m_c.find({'_id':ObjectId(note_id),'status':0}).count()
		return result

	def update_see_num(self,note_id):
		return self.m_c.update({'_id':ObjectId(note_id)},{"$inc":{"look_num":1}})

	def get_user_note(self,uid,page):
		page = int(page)
		per_page = int(options.note_per_page)
		uid = int(uid)
		note_cur = self.m_c.find({"uid":uid,'status':0},{'uid':0,'content':0}).sort([('time',-1)]).skip(page*per_page).limit(page)

		return list(note_cur)

	def delete_note(self,note_id):
		return self.m_c.update({'_id':ObjectId(note_id)},{"status":1})






 











