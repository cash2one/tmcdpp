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
from Models.usereventmodel import UserEventModel
from Models.gamemodel import GameModel
from Func.publicfunc import PublicFunc

class GameController:
	def __init__(self):
		self.gamemodel = GameModel()
		self.usersmodel = UsersModel()
		self.musermodel = MUserModel()



	def get_game_list(self,uid):
		game_list = self.gamemodel.get_game_list()
		for game_info in game_list:
			game_info['gacceptstartdate'] = PublicFunc.stamp_to_Ymd(game_info['gacceptstart'])
			game_info['gacceptenddate'] = PublicFunc.stamp_to_Ymd(game_info['gacceptend'])
			game_info['gfrontpage'] = options.ipnet + game_info['gfrontpage']
			game_info['agreement'] = options.ipnet + '/py/game?action=get_agreement&id=' + str(game_info['gid'])
			game_info['gstatusid'],game_info['gstatus'] = self.get_status_name(game_info['gstarttime'],game_info['gendtime'],game_info['gacceptstart'],game_info['gacceptend'])
			if game_info['gid'] == 7:
				game_info['gintro'] = options.ipnet + '/bjjbz/intro.bak.html?uid=' + str(uid)
				game_info['gintro_wecha'] = options.ipnet + '/bjjbz/intro.bak.html?uid=' + str(uid)
			if game_info['gid'] == 9:
				# game_info['gintro'] = 'http://mp.weixin.qq.com/s?__biz=MzI4MzM4MDM5MQ==&tempkey=6TdVDeLTjka%2FMedRgXr1jw5%2FEhRKAIdReyd2gYGoWvwCSJzZcVIQlw8ahYcN%2BhuSTga1LrgOwZ4xABg1O%2BbrtOuAdiWuSbVezSlYfihfUS3PSw1YoiJG8DhKWPiejoTWzHRVFZZrRPYejqkYKPGd1A%3D%3D&scene=1&srcid=0725qMCq5oIglvAmfbrXsUvp#wechat_redirect'
				# game_info['gintro_wecha'] = 'http://mp.weixin.qq.com/s?__biz=MzI4MzM4MDM5MQ==&tempkey=6TdVDeLTjka%2FMedRgXr1jw5%2FEhRKAIdReyd2gYGoWvwCSJzZcVIQlw8ahYcN%2BhuSTga1LrgOwZ4xABg1O%2BbrtOuAdiWuSbVezSlYfihfUS3PSw1YoiJG8DhKWPiejoTWzHRVFZZrRPYejqkYKPGd1A%3D%3D&scene=1&srcid=0725qMCq5oIglvAmfbrXsUvp#wechat_redirect'
				game_info['gintro'] = 'http://mp.weixin.qq.com/s?__biz=MzI4MzM4MDM5MQ==&mid=2247483830&idx=1&sn=a5e8ba2a262f3a1da7b65a5c18037315&scene=1&srcid=0725YTSd96e9sFKnqkH9AQZt#rd'
				game_info['gintro_wecha'] = 'http://mp.weixin.qq.com/s?__biz=MzI4MzM4MDM5MQ==&mid=2247483830&idx=1&sn=a5e8ba2a262f3a1da7b65a5c18037315&scene=1&srcid=0725YTSd96e9sFKnqkH9AQZt#rd'
			if game_info['gid'] == 10:
				game_info['gintro'] = 'http://mp.weixin.qq.com/s?__biz=MzI4MzM4MDM5MQ==&mid=2247483874&idx=1&sn=6371b0fd66106ce4e21650eb82b88090&scene=23&srcid=0729PXR5Q6FQFYiWnTr1vICx#rd'
				game_info['gintro_wecha'] = 'http://mp.weixin.qq.com/s?__biz=MzI4MzM4MDM5MQ==&mid=2247483874&idx=1&sn=6371b0fd66106ce4e21650eb82b88090&scene=23&srcid=0729PXR5Q6FQFYiWnTr1vICx#rd'
			else:
				game_info['gintro'] = options.ipnet + '/py/game?action=get_intro&id=' + str(game_info['gid']) + \
            	'&uid=' + str(uid) + '&gtype=' + str(game_info['gtype_id'])
            	game_info['gintro_wecha'] = options.ipnet + '/ky/game?action=get_intro&id=' + str(game_info['gid']) + \
            	'&uid=' + str(uid) + '&gtype=' + str(game_info['gtype_id'])
        	del game_info['gacceptstart']
        	del game_info['gacceptend']
		return game_list


	def get_game_status(self,uid,gid):
		"""
		get the game status,such as accept attend,attend stop,you have attend,etc !!!
		"""
		#判断用户是否已经报名了该赛事
		game_info = self.gamemodel.get_game_status(uid,gid)
		have_attend = UserEventModel().check_have_attend_game(uid,gid)
		if have_attend: return_dict = {'gstatusid':5,'gstatus':"已报名"}
		else:
			gstatusid,gstatus = self.get_status_name(game_info['gstarttime'],game_info['gendtime'],game_info['gacceptstart'],game_info['gacceptend'])
			return_dict = {'gstatusid':gstatusid,'gstatus':gstatus}
		return_dict['startmap'] = game_info['startmap']
		return_dict['sport_type'] = game_info['sport_type']
		return_dict['gid'] = gid
		return return_dict


	def get_status_name(self,gstarttime,gendtime,gacceptstart,gacceptend):
		"""
		根据时间参数获取赛事状态
		 gstatusid  0 game start  1 sign start   2 sign not start   3 sign end    4 game end  
		"""
		current_time = PublicFunc.get_current_stamp()
		if current_time > int(gendtime):return 4,"赛事结束"
		elif current_time > int(gstarttime): return 0,"赛事开始"
		elif current_time > int(gacceptend): return 3,"报名结束"
		elif current_time > int(gacceptstart): return 1,"接受报名"
		else: return 2,"报名未开始"






