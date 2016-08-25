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
import urllib2
import urllib
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
from Models.followmodel import FollowModel
from Models.organizationinfomodel import OrganizationInfoModel
from Models.organizationapplymodel import OrganizationApplyModel
from Models.organizationusermodel import OrganizationUserModel
from Func.publicfunc import PublicFunc

class OrgClubController:
	def __init__(self):
		pass

	def get_org_club_list(self,type,page):
		info = OrganizationInfoModel().get_org_club_list(type,page)
		for ele in info:
			ele['create_time'] = ele['create_time'][:10]
			ele['img_path'] = options.ipnet + ele['img_path']
			ele['athletics'] = ele['athletics'].split("|")[:3]
			star = self.get_star(ele['score'])
			ele['star_pic'] = self.get_star_pic(ele['score'])
		return info 

	def get_star(self,score):
		"""
		根据积分获取星级(共5级)
		"""
		scores = int(score)
		scores_list = [0,1000,3000,8000,20000]
		scores_list.append(int(score))
		scores_list.sort()
		return scores_list.index(score)

	def get_star_pic(self,score):
		star = self.get_star(score)
		return options.ipnet + '/staticPic/stars/' + str(star) + '.png' 

		# get_brief_info(a_d_m['id'])
	def get_brief_info(self,id):
		"""
		获取机构/俱乐部详细信息
		"""
		info = OrganizationInfoModel().get_brief_info(id)
		info['create_time'] = info['create_time'][:9]
		info['img_path'] = options.ipnet  + info['img_path']
		info['notice'] = info['notice'].split("||")
		info['athletics'] = info['athletics'].split('|')[:3]
		info['stars'] = self.get_star_pic(info['score'])
		info['need_check'] = 1 
		print info['join_type']
		return info 

	def search_by_id_name(self,search,page):
		"""
		"""
		info = OrganizationInfoModel().search_by_id_name(search,page)
		for ele in info:
			ele['create_time'] = ele['create_time'][:10]
			ele['img_path'] = options.ipnet + ele['img_path']
			ele['athletics'] = ele['athletics'].split("|")[:3]
			star = self.get_star(ele['score'])
			ele['star_pic'] = self.get_star_pic(ele['score'])
		return info


	def set_field(self,id,uid,field,new_value):
		is_admin = OrganizationUserModel().judge_is_admin(id,uid)
		if not is_admin: return "只有管理员可以更改机构/俱乐部信息"
		if field == 'join_type' and new_value not in set([0,1]):
			 return "join_type应该是0或者1"
		OrganizationInfoModel().set_field(id,field,new_value)
		return True

	def focus_org_oper(self,user_id,organization_id):
		focus_status = OrganizationUserModel().judge_has_focus(organization_id,user_id)
		if not focus_status:
			pass
			return ""
		else:
			pass
			return ""

	def attend_org(self,uid,id,excuse):
		need_check =OrganizationInfoModel().judge_need_check(id)
		is_member = OrganizationUserModel().judge_is_member(id,uid)
		if is_member: return "您已经在该机构中"
		OrganizationUserModel().set_user_member(id,uid)
		return "加入成功" if not int(need_check) else "审核中"










		
