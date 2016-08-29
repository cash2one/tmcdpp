#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import sys
import copy
import operator
import socket
from tornado.options import define, options
import json
import config
from  pdatabase import DbBase
from Func.publicfunc import PublicFunc
from tagmodel import TagModel
from usersmodel import UsersModel

class GameModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'fs_games_new'

	@classmethod
	def get_instance(cls):
		if not cls.model_instance: cls.model_instance = GameModel()
		return cls.model_instance

	def get_game_info(self,gid,param):
		"""
		function: 获取赛事信息
		author: yinshuai 
		input param:
				gid 赛事id
				param 查找的参数，param属性为列表
		return: 赛事信息字典
		"""
		game_info = self.find_data(param,get_some=False,gid=gid,status=0)
		return game_info


	def get_game_status(self,uid,gid):
		return self.find_data(['gstarttime','gendtime','gacceptstart','gacceptend','startmap','sport_type'],get_some=False,gid=gid,status=0)

	def get_game_list(self):
		return self.find_data(['*'],status=0,order=' sx desc ')

