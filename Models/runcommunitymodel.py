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
collection: runcommunity
structure:


_id 主键
gid 跑团对应的赛事id
comm_name 跑团名称
comm_member 跑团成员
         uid 成员用户id
         attend_time 成员加入时间 
         distance 成员运动距离(m)
         duration 成员运动时长(s)
         status  用户状态
member_num: 成员数量
create_time 创建时间
status 跑团状态


"""
class RunCommunityModel(MongoBase):
    """一个简单到模型，关于跑团和赛事互动的"""
    def __init__(self):
		MongoBase.__init__(self)
		self.m_c = self.mongo_db.runcommunity

    @classmethod 
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = RunCommunityModel()
    	return cls.model_instance

    def init_community(self):
    	# result = self.m_c.insert_one({'name':'yinshuai'}).inserted_id
    	self.m_c.insert_one({'gid':7,'comm_name':'劲松跑团','create_time':PublicFunc.get_current_stamp()})
    	self.m_c.insert_one({'gid':7,'comm_name':'18里店跑团','create_time':PublicFunc.get_current_stamp()})

    def create_community(self,gid,comm_name):
    	"""创建跑团"""
    	pass

    def update_run_data(self,comm_id,uid,distance,duration):
    	"""
    	function: 更新用户跑步数据
    	author: yinshuai
    	input param:
    	         uid:用户id 
    	         comm_id: 跑团主键id
    	         distance: 用户运动距离 
    	         duration: 运动时长
    	return: 
    	      True or except

    	""" 
    	uid = int(uid)
    	distance = int(distance)
    	duration = int(duration)
    	self.m_c.update({"_id":ObjectId(comm_id),"comm_member.uid":uid},{"$inc":{"comm_member.$.distance":distance,"comm_member.$.duration":duration}}) #set or inc
    	self.m_c.update({"_id":ObjectId(comm_id)},{"$push":{"comm_member":{"$each":[],"$sort":{"distance":-1}}}})
    	return True 

    def judge_user_in_comm(self,uid,comm_id):
    	"""
    	function: 判断用户是否在跑团里
    	author: yinshuai
    	input param: 
    	          uid:用户id 
    	         comm_id: 跑团主键id
    	return:
    	       True  在 
    	       False 不在
    	"""
    	uid = int(uid)
    	count = self.m_c.find({'_id':ObjectId(comm_id),'comm_member.uid':uid}).count()
    	return True if count else False 

    def attend_community(self,uid,comm_id):
    	""" 
    	function: 加入跑团 
    	author: yinshuai 
    	input param: 
    	         uid:用户id 
    	         comm_id: 跑团主键id
    	return_param: 
    	         True or except 
    	"""
    	uid = int(uid)
    	member_dict = {'uid':uid,'attend_time':PublicFunc.get_current_stamp()}
    	self.m_c.update({'_id':ObjectId(comm_id)},{'$inc':{"member_num":1},'$addToSet':{'comm_member':member_dict}})
    	return True

    def get_game_comm_belong(self,comm_id):
    	"""获取圈子所属到赛事   如果返回None表示不存在该跑团"""
    	return self.m_c.find_one({"_id":ObjectId(comm_id)},{"gid":1,'_id':0})['gid']

    def get_community_rank(self,comm_id,page):
    	"""
    	function: 获取圈子排名
    	author: yinshuai 
    	input param:
    	        comm_id 跑团主键id
    	        page 分页
    	return: 
    	        跑团用户排名数据
    	"""
    	page = int(page)
    	per_page = 10
    	# comm_run_list = self.m_c.find({"_id":ObjectId(comm_id)},{'uid':1,'distance':1,'_id':0}).sort([('distance',-1)]).skip(page*per_page).limit(per_page)
    	# comm_info = self.m_c.find({"_id":ObjectId(comm_id)},{'_id':0,'gid':0,'comm_name':0,'comm_member':{"$slice":[0,3]}})
    	# comm_info = self.m_c.find_one({"_id":ObjectId(comm_id)},{"$or":[{'comm_member':1},{'comm_member':{"$slice":[0,3]}}]})
    	comm_info = self.m_c.find_one({"_id":ObjectId(comm_id)},{'comm_member':{"$slice":[per_page*page,per_page]},'gid':1})
        comm_member = comm_info['comm_member']
    	for member_info in comm_member:
    		user_info = UsersModel.get_instance().get_import_user_info(member_info['uid'],['avatar','nickname'])
    		member_info['avatar'] = user_info['avatar']
        	if not 'distance' in member_info: member_info['distance'] = 0
    		member_info['nickname'] = user_info['nickname'] if user_info['nickname'] else '小跑男'
    	return comm_member




    def insert_some_test(self):
    	""" for test"""
    	for i in xrange(516,540):
    		run_length = int(''.join(sample('01002034567',6)))
    		# self.m_c.update({"gid"})
    		# self.m_c.insert({"gid":7,'uid':i,'comm_id':20,'distance':run_length,'duration':run_length,'recent_run_time':5555})
