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

class FCirController:
	def __init__(self):
		self.musermodel = MUserModel()
		self.usersmodel = UsersModel()

	def release_post(self,uid,pic_str,content,address,longitude,latitude):
		"""发布朋友圈说说"""
		pic_list = []
		for pic in pic_str.split(','):
			pic_path = pic[pic.index('/Uploads'):]
			pic_list.append(pic_path)
		pic_num = len(pic_list)
		post_id = PostModel().release_post(uid,pic_list,content,address,pic_num,longitude,latitude)
		return post_id

	def send_comment(self,uid,post_id,comm_content):
		"""
		function :  评论说说
		input param: 
				uid: 
				post_id 说说id  评论主键
				comm_content 评论内容 
		return: comm_id 评论pk
		"""
		comm_id = PostComModel().send_comment(uid,post_id,comm_content)
		PostModel().comm_num_oper(post_id,1)#更新说说评论总数
		PostModel().update_comm_list(uid,post_id,comm_content) #更新post集合中的第一页评论
		return comm_id

	def send_love(self,uid,post_id):
		result = PostLove().send_love(uid,post_id)
		if result == 'send_love':
			PostModel().love_oper(uid,post_id)
			return True
		return False #已经发送过了


	def get_post_info(self,post_id):
		"""
		获取说说详情
		"""
		post_info = PostModel().get_post_info(post_id)
		post_info['post_id'] = str(post_info['_id'])
		current_time = PublicFunc.get_current_stamp()
		post_info['time'] = PublicFunc.time_format_span(post_info['time'],current_time)
		del post_info['_id']
		user_info = UsersModel().get_import_user_info(post_info['uid'],['avatar','nickname'])#获取发说说的人的信息
		post_info['avatar'] = user_info['avatar']
		post_info['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		comm_list = post_info['comm_list']
		for comm in comm_list:
			comm['time'] = PublicFunc.time_format_span(comm['time'],current_time)
			comm_user_info =  UsersModel().get_import_user_info(comm['uid'],['avatar','nickname'])#获取评论说说的人的信息
			comm['avatar'] = comm_user_info['avatar']
			comm['nickname'] = comm_user_info['nickname'] if comm_user_info['nickname'] else options.default_nick_name
		love_list = post_info['love_list']
		for lover in love_list:
			lover_info = UsersModel().get_import_user_info(lover['uid'],['avatar','nickname'])#获取评论说说的人的信息
			lover['avatar'] = lover_info['avatar']
		post_info['pic_list'] = [options.ipnet + pic for pic in post_info['pic_list']]

		return post_info

	def get_recommend_list(self):
		"""
		获取推荐的关注列表
		"""
		user_list = UsersModel().get_double_user_info()
		for user in user_list:
			user['nickname'] = user['nickname'] if user['nickname'] else options.default_nick_name
			user['avatar'] = options.ipnet + user['avatar']
			user['run'] = 333
		return user_list




	def get_post_list(self,uid,page):
		"""
		function: 获取说说列表
		"""
		post_list = PostModel().get_post_list(page)
		current_time = PublicFunc.get_current_stamp()
		for post in post_list:
			post['post_id'] = str(post['_id'])
			post['have_love'] = 1 if PostLove().judge_post_love(uid,post['_id']) else 0 
			del post['_id']
			post['pic_list'] = [{'ori_pic':options.ipnet + pic,'thumb_pic':options.ipnet+options.post_thumb_save_path+'t'+pic[-17:]} for pic in post['pic_list']]
			post['time'] = PublicFunc.time_format_span(post['time'],current_time)
			user_info = UsersModel().get_import_user_info(post['uid'],['avatar','nickname'])
			post['avatar'] = user_info['avatar']
			post['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		return post_list

	def get_lover_list(self,post_id,page):
		""" 获取说说喜欢用户列表"""
		lover_list = PostLove().get_lover_list(post_id,page)
		current_time = PublicFunc.get_current_stamp()
		for lover in lover_list:
			del lover['_id']
			del lover['post_id']
			lover['time'] = PublicFunc.time_format_span(lover['time'],current_time)
			user_info = UsersModel().get_import_user_info(lover['uid'],['avatar','nickname'])
			lover['avatar'] = user_info['avatar']
			lover['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
		return lover_list

	def judge_post_exist(self,post_id):
		"""判断是否存在该帖子"""
		result = PostModel().get_post_num(post_id)
		return True if result else False

	def get_user_post(self,uid,page):
		"""获取用户的朋友圈"""
		post_list = PostModel().get_user_post(uid,page)
		current_time = PublicFunc.get_current_stamp()
		is_today = 1 # 默认是今天
		for post in post_list:
			post['post_id'] = str(post['_id'])
			del post['_id'] 
			if not PublicFunc.get_date_today() == PublicFunc.stamp_to_Ymd(post['time']):is_today = 0
			post['is_today'] = is_today
			date_info = PublicFunc.get_date_info(post['time'],['day','month'])
			post['pic_list'] = [{'ori_pic':options.ipnet + pic,'thumb_pic':options.ipnet+options.post_thumb_save_path+'t'+pic[-17:]} for pic in post['pic_list']]
			post['day'] = date_info['day']
			post['month'] = date_info['month']
		return post_list







