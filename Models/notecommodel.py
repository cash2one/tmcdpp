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
collection: notecomment  帖子评论模型  
structure:

_id 主键
uid  用户id 也就是对帖子或者对其他人的评论发起评论的人
note_id 帖子id
comm_content 评论内容
agree_num 点赞总数
agree_uid_li 点赞用户列表
content 回复内容
time 回复时间
status 帖子状态

"""
class NoteComModel(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.notecomment

	def get_instance(cls):
		if not cls.model_instance:cls.model_instance = NoteComModel()
		return cls.model_instance

	def make_comment(self,note_id,uid,comm_content):
		"""给帖子做评论"""
		current_time = PublicFunc.get_current_stamp()
		com_dict = {'note_id':note_id,'uid':uid,'comm_content':comm_content,'time':current_time,'status':0,'agree_num':0}
		return str(self.m_c.insert(com_dict))

	def agree_comment(self,uid,comm_id):
		"""为用户对帖子的评论点赞"""
		uid = int(uid)
		agree_info = self.m_c.find_one({'_id':ObjectId(comm_id)},{'agree_uid_li':-1,'_id':0})
		if agree_info:#如果有人赞过了，那么看这个人有没有赞过哦
			uid_set = set(agree_info['agree_uid_li'])	
			if uid in uid_set:return False
		self.m_c.update({'_id':ObjectId(comm_id)},{'$inc':{'agree_num':1},'$push':{'agree_uid_li':uid}})
		return True

	def get_note_comm(self,note_id,page):
		"""
		function: 获取帖子的评论
		input param: 
		         note_id: 帖子id  
		         page 分页
		return xxx
		"""
		page = int(page)
		comm_per_page = int(options.note_comm_per_page)
		comm_list = self.m_c.find({'note_id':note_id,'status':0}).sort([('time',-1)]).skip(comm_per_page*page).limit(comm_per_page)
		comm_list = list(comm_list)
		return comm_list

	def get_comment_num(self,comm_id):
		return self.m_c.find({"_id":ObjectId(comm_id),'status':0}).count()





