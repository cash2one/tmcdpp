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
collection: postcomment  说说评论模型  
structure:

_id 主键
uid  用户id 
post_id 帖子id
comm_content 评论内容
time 评论时间
status 帖子状态

"""
class PostComModel(MongoBase):
	def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.postcomment

	def get_comment_list(self,post_id,page):
		"""获取说说评论列表"""
		pass

	def send_comment(self,uid,post_id,comm_content):
		"""发布评论"""
		comm_id = self.m_c.insert({'uid':uid,'post_id':post_id,'comm_content':comm_content,'status':0,'time':int(time.time())})
		return str(comm_id)

