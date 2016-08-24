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
		act_per_page = self.find_data(['regis_start_time','regis_end_time','start_time','end_time','name','organization_id','logo_img','regist_member','regis_cost','classify','regist_member','address_address'],get_some=(jump,act_per_page),organization_id=id)
		return act_per_page		