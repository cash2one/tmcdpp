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
from Func.publicfunc import PublicFunc
from usersmodel import UsersModel
from  pdatabase import DbBase

class ActivitySignUpModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'activity_sign_up'

	def judge_have_attend(self,user_id,activity_id):
		"""
		根据用户手机号和姓名判断用户是否已经报名了活动
		"""
		return self.find_db_sum(user_id=user_id,activity_id=activity_id)


	def attend_activity(self,activity_id,user_id,truename,tel,sex):
		create_time = PublicFunc.get_current_datetime()
		info_dict = {"activity_id":activity_id,"user_id":user_id,"truename":truename,"tel":tel,"sex":sex,"create_time":create_time}
		self.insert_into_db(info_dict)
		return True

	def get_attend_list(self,activity_id,page):
		per_page = int(options.act_attend_per_page)
		jump = per_page*int(page)
		return self.find_data(['user_id','truename'],get_some=(jump,per_page),activity_id=activity_id)

