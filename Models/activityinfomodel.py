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

class ActivityInfoModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'activity_info'

	def get_act_list(self,id,page):
		"""
		"""
		act_per_page = int(options.act_per_page)
		jump = int(page) * act_per_page
		act_per_page = self.find_data(['id','regis_start_time','regis_end_time','start_time','end_time','name','organization_id','logo_img','regist_member','regis_cost','classify','regist_member','address_address'],get_some=(jump,act_per_page),organization_id=id)
		return act_per_page	

	def get_agree_list(self,id):
		"""
		get the likelist of the activity
		"""
		return self.find_data(['like_list'],get_some=False,id=id)['like_list']

	def set_agree_list(self,id,like_list):
		return self.update_db({'like_list':like_list},organization_id=id)

	def get_act_info(self,activity_id):
		act_info = self.find_data(['sponsor_sponsor','start_time','end_time','name','introduce_introduce','regist_notice','activity_rule','address_address','regis_start_time','regis_end_time','regist_member','regis_max'],get_some=False,id=activity_id)
		return act_info



