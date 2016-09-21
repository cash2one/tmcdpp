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
		return self.find_data(['id','members','create_time','img_path','athletics','score','name','`desc`'],get_some=(jump,org_per_page),order=' score desc ',type=type)



	def get_brief_info(self,id):
		return self.find_data(['intro','`desc`','athletics','name','score','create_time','address','type','img_path','notice','members','id','join_type','concern'],get_some=False,id=id)

	def set_field(self,id,field,new_value):
		"""
		只可以修改宣言和加入方式
		"""
		if field  == 'desc': field = '`desc`'
		return self.update_db({field:new_value},id=id)

	def search_by_id_name(self,search,page):
		org_per_page = options.org_per_page
		org_per_page = 10
		jump = int(page) * int(org_per_page)
		part1 = self.find_data(['members','create_time','img_path','athletics','score','name','id'],get_some=(jump,org_per_page),order=' score desc ',id={'rule':'like','value':str(search)})
		part2 = self.find_data(['members','create_time','img_path','athletics','score','name','id'],get_some=(jump,org_per_page),order=' score desc ',name={'rule':'like','value':str(search)})
		return part2 + part1


	def judge_need_check(self,organization_id):
		return self.find_data(['join_type'],get_some=False,id=organization_id)['join_type']


