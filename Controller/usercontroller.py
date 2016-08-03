#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import sys
import random
import hashlib
import requests
import urllib2
import urllib
from random import sample
import copy
import tornado.autoreload 
import operator
import socket
from tornado.options import define, options
import json
import config
from Models.usersmodel import UsersModel
from Models.musermodel import MUserModel
from Models.notemodel import NoteModel
from Models.notecommodel import NoteComModel
from Models.postmodel import PostModel
from Models.postcommodel import PostComModel
from Models.interestmodel import InterestModel
from Models.rundatamodel import RunDataModel
from Models.groupmodel import GroupModel
from Models.followmodel import FollowModel
from Func.publicfunc import PublicFunc
# from Func.publicfunc import PublicFunc
from bson.objectid import ObjectId

class UserController:
	def __init__(self):
		self.usersmodel = UsersModel()
		self.musermodel = MUserModel()

	def login(self,tel,password):
		"""
		用户登录接口，登录成功之后要判断mongo里面是否有这个用户了，如果没有的话，新建
		"""
		user_exist = UsersModel().check_tel_register(tel)
		if not user_exist: return 0#用户还没有注册
		login_info  = self.usersmodel.login(tel,password) #mysql  
		if not password == login_info['password']: return 1 #
		#if the user has not clear the token before!! then continue use this token!!
		token = login_info['token']
		if not token:
			token = PublicFunc.create_token(login_info['uid'])
		change_param = {'token':token,'login_times':login_info['login_times']+1,'last_login':int(time.time())}
		self.usersmodel.update_db(change_param,tel=tel)
		self.usersmodel.clear_user_cache(login_info['uid'])
		self.usersmodel.cache_import_user_info(login_info['uid'])
		bind_layer_show = 1 if self.usersmodel.judge_show_bind_layer(login_info['uid']) else 0
		return token,login_info['uid'],bind_layer_show

	def person_center(self,uid,other_uid):
		"""
		获取用户个人中心的信息
		uid 用户id  other_id 所打开的其他人的id
		"""
		uid = int(uid)
		other_uid = int(other_uid)
		# person_center = self.musermodel.person_center(uid)
		person_center = self.musermodel.person_center(other_uid)
		for following in person_center['following_list']:
			user_info = self.usersmodel.get_import_user_info(following['uid'],['avatar','nickname'])
			following['avatar'] = user_info['avatar']
			following['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		for follower in person_center['follower_list']:
			user_info = self.usersmodel.get_import_user_info(follower['uid'],['avatar','nickname'])
			follower['avatar'] = user_info['avatar']
			follower['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		user_info = self.usersmodel.get_import_user_info(other_uid,['avatar','nickname'])
		person_center['avatar'] = user_info['avatar']
		person_center['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		person_center['ready_id'] = '100' + str(uid)
		sum_run_info = RunDataModel().get_user_sum_run(uid)
		if sum_run_info:
			person_center['run_duration'] = round(sum_run_info['duration']/3600.0,1)
			person_center['run_distance'] = round(sum_run_info['distance']/1000.0,1)
		else:
			person_center['run_duration'] = 0
			person_center['run_distance'] = 0
		if not uid == other_uid:
			person_center['has_follow'] = '已关注' if FollowModel().get_follow_status(uid,other_uid) else '关注'
		person_center['interest'] = [iname['iname'] for iname in InterestModel().get_user_interest(uid)]
		person_center['group_num'] =  GroupModel().get_group_num(uid) 
		group_list = GroupModel().get_some_group(uid,options.group_get_num)
		for group in group_list:
			group['avatar'] = options.ipnet + group['avatar']
		person_center['group_list'] = group_list
		if 'cir_back' in person_center:
			person_center['cir_back'] = options.ipnet + person_center['cir_back']
		else:
			person_center['cir_back'] = options.ipnet + '/Uploads/back.jpg'
		return person_center

	def update_cir_back(self,uid,pic_path):
		"""更新用户朋友圈背景图"""
		#treat
		self.musermodel.update_cir_back(uid,pic_path)



