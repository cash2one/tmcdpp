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
from Models.postlovemodel import PostLove
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

	def person_center(self,uid):
		"""获取用户个人中心的信息"""
		uid = int(uid)
		person_center = self.musermodel.person_center(uid)
		for following in person_center['following_list']:
			user_info = self.usersmodel.get_import_user_info(following['uid'],['avatar','nickname'])
			following['avatar'] = user_info['avatar']
			following['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		for follower in person_center['follower_list']:
			user_info = self.usersmodel.get_import_user_info(follower['uid'],['avatar','nickname'])
			follower['avatar'] = user_info['avatar']
			follower['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		user_info = self.usersmodel.get_import_user_info(uid,['avatar','nickname'])
		person_center['avatar'] = user_info['avatar']
		person_center['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		person_center['ready_id'] = '100' + str(uid)
		person_center['run_duration'] = 2.5 
		person_center['run_distance'] = 250
		person_center['interest'] = ['跑步','健走','足球']  
		person_center['group_num'] = 25
		person_center['group_list'] = [] 
		group_info = {'group_name':'测试团队','group_id':25,'avatar':'http://101.200.214.68/Uploads/group.jpg'}
		person_center['group_list'].append(group_info)
		person_center['group_list'].append(group_info)
		person_center['cir_back'] = options.ipnet + person_center['cir_back']

		return person_center

	def update_cir_back(self,uid,pic_path):
		"""更新用户朋友圈背景图"""
		#treat
		self.musermodel.update_cir_back(uid,pic_path)



