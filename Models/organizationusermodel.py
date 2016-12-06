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
		self.is_admin = 4 #是否是管理员 
		self.has_focus = 1# 是否已经关注
		self.is_ord_memeber = 2 #是否是普通成员
		self.is_applying = 32# 



	def get_user_role(self,uid,org_id):
		"""
		获取用户角色
		"""
		info = self.find_data(['type'],organization_id=org_id,user_id=uid,get_some=False)
		if not info: return 0#not the member of the organization 
		role_field = int(info['type'])
		if role_field & self.is_admin: return 1 # is admin 
		elif role_field & self.is_ord_memeber: return 2 #is ord_member
		elif role_field & self.is_applying: return 3 #is applying 
		else: return 0


	def judge_is_admin(self,organization_id,user_id):
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if not info: return False
		return True if int(info['type']) & self.is_admin  else False 

	def judge_has_focus(self,organization_id,user_id):
		"""
		return True if has focus else False 
		"""
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if not info:
			self.insert_into_db({'user_id':user_id,'organization_id':organization_id,'msg':'','type':0,'change_date':PublicFunc.get_current_datetime()}) 
			return False
		return True if int(info['type']) &  (self.has_focus + self.is_admin + self.is_ord_memeber) else False 

	def get_my_org_club_list(self,uid,page):
		per_page = options.org_per_page
		jump = int(page) * int(per_page)
		is_mem = str(self.is_admin + self.is_ord_memeber + self.has_focus)
		sql = 'select organization_id,type from ' + self.table + ' where user_id=' + str(uid) + ' and type & ' + is_mem  + \
			   " >0   order by type desc limit " + str(jump) + ',' + str(per_page)
		return self.sql_select(sql)


	def add_focus(self,organization_id,user_id):
		sql = "update %s set type = type | %s where organization_id=%s and user_id=%s" % (self.table, self.has_focus,organization_id,user_id)
		return self.sql_update(sql)

	def cancel_focus(self,organization_id,user_id):
		sql = "update %s set type = type ^ %s where organization_id=%s and user_id=%s" % (self.table, self.has_focus,organization_id,user_id)
		return self.sql_update(sql)

	def judge_is_member(self,organization_id,user_id):
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if not info:return False
		return True if int(info['type']) & (self.is_admin | self.is_ord_memeber)  else False

	def judge_user_role(self,organization_id,user_id):
		"""
		判断用户角色
		"""
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if info is None:
			return False#not this data row 
		type = int(info['type'])
		if type & self.is_admin: return 0 ## is admin 
		if type & self.is_ord_memeber: return 1 ##ord_member 
		if type & self.is_applying: return 2 ##applying 
		return False

	def set_user_member(self,organization_id,user_id,excuse):
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if not info:#如果没有该条数据
			info = {}
			info['type'] = 0
			self.insert_into_db({"organization_id":organization_id,"user_id":user_id,"type":self.is_ord_memeber,"msg":excuse,"change_date":PublicFunc.get_current_datetime()})
			return
		new_type = info['type'] | self.is_ord_memeber
		return self.update_db({'type':new_type},organization_id=organization_id,user_id=user_id,msg=excuse,change_date=PublicFunc.get_current_datetime())

	def set_user_apply(self,organization_id,user_id,excuse):
		"""
		设置用户为申请状态
		"""
		info = self.find_data(['type'],organization_id=organization_id,user_id=user_id,get_some=False)
		if not info:#如果没有该条数据
			info = {}
			info['type'] = 0
			self.insert_into_db({"organization_id":organization_id,"user_id":user_id,"type":self.is_applying,"msg":excuse,"change_date":PublicFunc.get_current_datetime()})
			return
		new_type = info['type'] | self.is_applying
		return self.update_db({'type':new_type},organization_id=organization_id,user_id=user_id)


	def get_apply_list(self,id,page):
		"""
		"""
		per_page = int(options.apply_per_page)###3 
		jump = per_page * int(page)
		sql = 'select user_id,change_date,msg,id from %s where organization_id = %s and type & %s = %s  order by change_date desc  limit %s,%s' % (self.table,id,self.is_applying,self.is_applying,jump,per_page)
		return self.sql_select(sql)

	def pass_apply(self,apply_id):
		"""
		"""
		sql = 'update %s set type = type ^ %s where id = %s' % (self.table,self.is_ord_memeber + self.is_applying,apply_id)
		return self.sql_update(sql)

	def ignore_apply(self,apply_id):
		sql = 'update %s set type = type & %s where id = %s' % (self.table,self.is_applying,apply_id)
		return self.sql_update(sql)


	def get_member_list(self,organization_id,page):
		per_page = 12 #each page show 12 
		jump = per_page * int(page)
		sql = "select user_id,type from %s where organization_id=%s and type & 6 > 0 limit %s,%s" % (self.table,organization_id,jump,per_page)
		return self.sql_select(sql)









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


