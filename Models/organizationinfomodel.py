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

class OrganizationInfoModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'organization_info'

	def search_by_name_or_id(self,search_item,page):
		"""
		根据名称或者ｉｄ搜索　俱乐部或者机构
		"""
		pass

	def get_org_club_list(self,type,page):
		"""
		获取机构/俱乐部列表
		"""
		org_per_page = options.org_per_page
		jump = int(page) * int(org_per_page)
		return self.find_data(['members','create_time','img_path','athletics','score','name'],get_some=(jump,org_per_page),order=' score desc ',type=type)
