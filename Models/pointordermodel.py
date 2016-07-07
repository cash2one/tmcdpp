#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import tornado.options
import tornado.web
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
from  pdatabase import DbBase
from usersmodel import UsersModel
sys.path.append("..")
from Func.publicfunc import PublicFunc

class PointOrderModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'fs_point_order'

	@classmethod
	def get_instance(cls):
		if not cls.model_instance: cls.model_instance = PointOrderModel()
		return cls.model_instance

	def save_order(self,param_dict):
		"""保存订单数据"""
		return self.insert_into_db(param_dict)

	def change_order_status(self,orderNum,new_status):
		"""修改订单状态   default0   has_pay:1  not_pay:2    new_status(true,false) """
		order_info = self.find_data(['pay_status','uid','credits'],get_some=False,orderNum=orderNum)
		order_status = order_info['pay_status']
		if not order_status: #只有订单状态没有发生任何改变才会修改订单状态
		    change_into = 2 if new_status == 'false' else 1
		    self.update_db({'pay_status':change_into},orderNum=orderNum)
		    if new_status == 'false':  #如果回调的数据是失败的，那么返回用户积分
		        UsersModel.get_instance().change_user_point(order_info['uid'],order_info['credits']) #返还用户积分（如果失败）
		return True

	def get_reward_list(self,page):
		page = int(page)
		per_page = 30
		reward_list = self.find_data(['description','timestamp','id','uid'],get_some=(page*5,per_page)) #aaaaaaa
		current_time = PublicFunc.get_current_stamp()
		for index,reward in enumerate(reward_list):
			user_info = UsersModel.get_instance().get_import_user_info(reward['uid'],['avatar','nickname'])
			reward_list[index]['nickname'] = '小跑男' if not user_info['nickname']  else user_info['nickname']  
			reward_list[index]['avatar'] = user_info['avatar']
			reward_list[index]['time'] = PublicFunc.time_format_span(str(reward['timestamp'])[:-3],current_time) 
			del reward_list[index]['timestamp']
		return reward_list





