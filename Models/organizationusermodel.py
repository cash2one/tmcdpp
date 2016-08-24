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

class OrganizationUserModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'organization_user'
		self.is_admin = 4 

	def judge_is_admin(self,organization_id,user_id):
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if not info: return False
		return True if int(info['type']) & self.is_admin  else False 

	# def search_by_name_or_id(self,search_item,page):
	# 	"""
	# 	根据名称或者ｉｄ搜索　俱乐部或者机构
	# 	"""
	# 	pass

	# def get_org_club_list(self,type,page):
	# 	"""
	# 	获取机构/俱乐部列表
	# 	"""
	# 	org_per_page = options.org_per_page
	# 	jump = int(page) * int(org_per_page)
	# 	return self.find_data(['members','create_time','img_path','athletics','score','name'],get_some=(jump,org_per_page),order=' score desc ',type=type)

	# def get_brief_info(self,id):
	# 	return self.find_data(['intro','`desc`','athletics','name','score','create_time','img_path','notice','members','id'],get_some=False,id=id)

	# def set_field(self,id,field,new_value):
	# 	"""
	# 	只可以修改宣言和加入方式
	# 	"""
	# 	return self.update_db({field:new_value},id=id)

	# def search_by_id_name(self,search,page):
	# 	org_per_page = options.org_per_page
	# 	jump = int(page) * int(org_per_page)
	# 	part1 = self.find_data(['members','create_time','img_path','athletics','score','name'],get_some=(jump,org_per_page),order=' score desc ',id={'rule':'like','value':str(search)})
	# 	part2 = self.find_data(['members','create_time','img_path','athletics','score','name'],get_some=(jump,org_per_page),order=' score desc ',name={'rule':'like','value':str(search)})
	# 	return part2 + part1


