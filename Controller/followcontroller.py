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
from Models.followmodel import FollowModel
from Func.publicfunc import PublicFunc
# from Func.publicfunc import PublicFunc
from bson.objectid import ObjectId

class FollowController:
	def __init__(self):
		self.followmodel = FollowModel()
		self.usersmodel = UsersModel()
		self.musermodel = MUserModel()

	def following_man(self,uid,fuid):
		"""
		function: 成为其他用户的粉丝,这里不仅仅要修改自己的关注列表，也要将自己设置为其他人的粉丝
		input param:
				uid 粉丝uid
				fuid 被关注的人的id
		"""
		if not self.usersmodel.judge_uid_exist(uid):
			return 'uid为' + uid + '的用户不存在'
		if not self.usersmodel.judge_uid_exist(fuid):
			return 'uid为' + fuid + '的用户不存在'
		result = self.followmodel.following_man(uid,fuid)
		if result == 'follow_success':
			MUserModel().add_following(uid,fuid) #修改自己的关注列表
			MUserModel().add_follower(fuid,uid) #修改被关注用户的的粉丝列表
			return '取消关注'
		elif result == 'cancel_success':
			# print 'start cancel'
			MUserModel().cancel_following(uid,fuid) #取消自己所关注的人
			# MUserModel().cancel_follower(uid,fuid) #自己不再是别人的粉丝了 ####################################################################################################
			return '关注'



	def follow_other(self,uid,fuid):
		"""
		关注他人，只具有关注功能
		"""
		if not self.usersmodel.judge_uid_exist(uid):
			return 'uid为' + uid + '的用户不存在'
		if not self.usersmodel.judge_uid_exist(fuid):
			return 'uid为' + fuid + '的用户不存在'
		if self.followmodel.follow_other(uid,fuid):
			MUserModel().add_following(uid,fuid) #修改自己的关注列表
			MUserModel().add_follower(fuid,uid) #修改被关注用户的的粉丝列表
			return '已关注'
		else:
			return '已关注'






	def get_following_list(self,uid,page):
		"""获取我所关注的人的列表"""
		following_list = self.followmodel.get_following_list(uid,page)
		current_time = PublicFunc.get_current_stamp()
		for f in following_list:
			f['time'] = PublicFunc.time_format_span(f['time'],current_time)
			user_info = UsersModel().get_import_user_info(f['fuid'],['avatar','nickname'])
			f['avatar'] = user_info['avatar']
			f['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		return following_list

	def get_follower_list(self,uid,page):
		"""获取粉丝列表"""
		follower_list = self.followmodel.get_follower_list(uid,page)
		current_time = PublicFunc.get_current_stamp()
		for f in follower_list:
			f['time'] = PublicFunc.time_format_span(f['time'],current_time)
			user_info = UsersModel().get_import_user_info(f['uid'],['avatar','nickname'])
			f['avatar'] =  user_info['avatar']
			f['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		return follower_list

