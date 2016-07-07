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
from Func.publicfunc import PublicFunc
# from Func.publicfunc import PublicFunc
from bson.objectid import ObjectId

class NoteController:
	def __init__(self):
		self.notemodel = NoteModel()
		self.musermodel = MUserModel()


	def get_note_info(self,note_id):
		"""
		function: 获取帖子信息 这里在获取帖子的评论的时候，默认获取首页数据
		input param: 
				note_id 帖子id
		"""
		note_basic_info = NoteModel().get_note_info(ObjectId(note_id))#获取帖子基本信息
		note_user_info = UsersModel().get_import_user_info(note_basic_info['uid'],['avatar','nickname'])#获取发帖人信息
		note_basic_info['avatar'] = note_user_info['avatar']
		note_basic_info['nickname'] = note_user_info['nickname']
		note_comm_list = NoteComModel().get_note_comm(note_id,0)#获取评论信息
		note_comm_num = note_basic_info['com_num']
		current_time = PublicFunc.get_current_stamp()
		for comm in note_comm_list:
			comm['comm_id'] = str(comm['_id'])
			user_info = UsersModel().get_import_user_info(comm['uid'],['avatar','nickname'])
			comm['avatar'] = user_info['avatar']
			comm['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
			comm['level'] = note_comm_num
			comm['time'] = PublicFunc.time_format_span(comm['time'],current_time)
			note_comm_num -= 1
			del comm['_id']
			del comm['note_id']
		return note_basic_info,note_comm_list

	def make_comment(self,note_id,uid,comm_content):
		"""给帖子做评论"""
		NoteModel().update_note_comm_num(note_id,1) #评论总数加1
		return NoteComModel().make_comment(note_id,uid,comm_content)
		

	def get_note_comm(self,note_id,page):
		"""
		function: 获取帖子的评论
		input param: 
		         note_id: 帖子id  
		         page 分页
		return xxx
		"""
		comm_num = NoteModel().get_note_comm_num(note_id)
		page = int(page)
		comm_per_page = int(options.note_comm_per_page)
		level = comm_num - page*comm_per_page
		note_comm_list = NoteComModel().get_note_comm(note_id,page)
		current_time = PublicFunc.get_current_stamp()
		for comm in note_comm_list:
			comm['comm_id'] = str(comm['_id'])
			user_info = UsersModel().get_import_user_info(comm['uid'],['avatar','nickname'])
			comm['avatar'] = user_info['avatar']
			comm['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
			comm['level'] = level
			level -= 1 
			comm['time'] = PublicFunc.time_format_span(comm['time'],current_time)
			del comm['_id']
			del comm['note_id']
		return note_comm_list

	def judge_note_exist(self,note_id):
		"""
		判断帖子是否存在
		"""
		result = NoteModel().get_note_num(note_id)
		return True if result else False

	def judge_comm_exist(self,comm_id):
		"""判断帖子的评论是否存在"""
		result = NoteComModel().get_comment_num(comm_id)
		return True if result else False

	def agree_comment(self,uid,comm_id):
		"""为帖子的评论点赞"""
		result = NoteComModel().agree_comment(uid,comm_id)
		return 'has_agree' if result else 'agree'

	def update_see_num(self,note_id):
		"""更新帖子查看数"""
		return NoteModel().update_see_num(note_id)

	def get_user_note(self,uid,page):
		"""获取我的帖子列表"""
		uid = int(uid)
		note_list = NoteModel().get_user_note(uid,page)
		current_time = PublicFunc.get_current_stamp()
		for note in note_list:
			note['note_id'] = str(note['_id'])
			del note['_id']
			note['time'] = PublicFunc.time_format_span(note['time'],current_time)
		return note_list

	def release_note(self,uid,title,content):
		""" 发布帖子"""
		note_id = self.notemodel.release_note(uid,title,content)
		self.musermodel.add_note(uid,note_id,title)
		return note_id








