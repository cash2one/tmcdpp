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
from Models.activityinfomodel import ActivityInfoModel
from Models.activitysignupmodel import ActivitySignUpModel
from Func.publicfunc import PublicFunc

class ActController:
	def __init__(self):
		pass

  # `crowner_crowner` varchar(512) DEFAULT NULL COMMENT '冠名单位（文字），多个用“||”分割',
  # `regis_start_time` varchar(19) DEFAULT NULL COMMENT '报名开始时间（yyyy-MM-dd HH:mm:ss）周期内可报名，可与活动周期重叠',
  # `regis_end_time` varchar(19) DEFAULT NULL COMMENT '报名结束时间（yyyy-MM-dd HH:mm:ss）',
  # `start_time` varchar(19) DEFAULT NULL COMMENT '活动开始时间（yyyy-MM-dd HH:mm:ss）',
  # `end_time` varchar
	def get_act_status(self,regis_start_time,regis_end_time,start_time,end_time):
		current_datatime = PublicFunc.get_current_datetime()
		if current_datatime < regis_start_time: return {'flag':0,'name':'预告'}
		if current_datatime < regis_end_time: return {'flag':1,'name':'报名中'}
		if current_datatime < start_time: return {'flag':2,'name':'马上开始'} 
		if current_datatime < end_time: return {'flag':3,'name':'进行中'}   
		else: return {'flag':4,'name':'已结束'} 
		return '结束' 


	def get_act_list(self,id,page):
		"""
		根据输入的机构id来获取该机构/俱乐部所管辖的赛事列表
		"""
		act_list =  ActivityInfoModel().get_act_list(id,page)
		for act in act_list:
			act_info_status = self.get_act_status(act['regis_start_time'],act['regis_end_time'],act['start_time'],act['end_time'])
			act['act_status'] = act_info_status['name']
			act['act_status_id'] = act_info_status['flag'] 
			act['time_scope'] = act['start_time'][5:16] + ' - ' + act['end_time'][5:16]
			act['logo_img'] = options.ipnet + act['logo_img']
			if not int(act['regis_cost']):act['regis_cost'] = '免费' 
			act['classify'] = act['classify'].split("|")[:int(options.classify_num_show)]
		return act_list

	def agree_act(self,id,uid):
		"""
		给喜欢的活动点赞
		"""
		like_list_str= '|' + ActivityInfoModel().get_agree_list(id) + '|'
		search_str = '|' + str(uid) + '|'
		if search_str in like_list_str :return '您已经点赞了'
		new_like_list_str = like_list_str + str(uid)
		ActivityInfoModel().set_agree_list(id,new_like_list_str)
		return True

		# ).get_agree_list(self,a_d_m['id'],a_d_m['page'])

	def get_agree_list(self,id,page):
		per_page = int(options.act_agree_per_page)
		page = int(page)
		agree_uid_list = ActivityInfoModel().get_agree_list(id).split('|')[per_page*page:per_page*(page+1)]
		agree_user_list = []
		for uid in agree_uid_list:
			user_info = UsersModel().get_import_user_info(uid,['avatar','nickname','uid'])
			if not user_info['nickname']: user_info['nickname'] = options.default_nick_name
			agree_user_list.append(user_info)
		return_list = {}
		return_list['per_page'] = per_page
		return_list['agree_num'] = 5256#####################################################################################=======================================================================
		return_list['agree_list'] = agree_user_list
		return return_list

	# def attend_act(a_d_m['activity_id'],a_d_m['truename'],a_d_m['sex'],a_d_m['tel'])
	def attend_act(self,uid,activity_id,truename,sex,tel):
		has_attend = ActivitySignUpModel().judge_have_attend(uid,activity_id)
		if int(has_attend): return "您已经报过名了"
		else:
			ActivitySignUpModel().attend_activity(activity_id,uid,truename,tel,sex)
			avatar = UsersModel().get_import_user_info(uid,['avatar'])['avatar']
			# content = truename
			# save_message_info(self,type,target_id,title,,avatar,""):

	def get_act_info(self,uid,activity_id):
		act_info = ActivityInfoModel().get_act_info(activity_id)
		act_info['time_scope'] = act_info['start_time'][5:-2] + " "  + act_info['end_time'][5:-2]
		act_info_status = self.get_act_status(act_info['regis_start_time'],act_info['regis_end_time'],act_info['start_time'],act_info['end_time'])
		act_info['activity_status'] = act_info_status['name']
		act_info['activity_status_id'] = act_info_status['flag']
		act_info['regist_avail'] = act_info['regis_max'] - act_info['regist_member'] 
		act_info['has_attend'] = '已报名' if int(ActivitySignUpModel().judge_have_attend(uid,activity_id)) else '报名'
		return act_info

	def get_attend_list(self,activity_id,page):
		per_page = options.act_attend_per_page# 8 
		# return_list = [] 
		# return_list['per_page'] = per_page
		attend_uid_list = ActivitySignUpModel().get_attend_list(activity_id,page)
		attend_list_return = {}
		attend_list_return['per_page'] = per_page
		attend_user_info = []
		for user in attend_uid_list:
			user_info = UsersModel().get_import_user_info(user['user_id'],['avatar'])
			user_info['uid'] = user['user_id']
			user_info['truename'] = user['truename']
			user_info['create_time'] = user['create_time'][:16]
			attend_user_info.append(user_info)
		attend_list_return['attend_list'] = attend_user_info
		return attend_list_return






