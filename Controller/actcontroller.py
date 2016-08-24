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
		if current_datatime < regis_start_time: return '预告'
		if current_datatime < regis_end_time: return '报名中'
		if current_datatime < start_time: return '未开始' 
		if current_datatime < end_time: return '进行中'    
		return '结束' 


	def get_act_list(self,id,page):
		"""
		根据输入的机构id来获取该机构/俱乐部所管辖的赛事列表
		"""
		act_list =  ActivityInfoModel().get_act_list(id,page)
		for act in act_list:
			act['act_statuc'] = self.get_act_status(act['regis_start_time'],act['regis_end_time'],act['start_time'],act['end_time'])
			act['time_scope'] = act['start_time'][5:16] + ' - ' + act['end_time'][5:16]
			act['logo_img'] = options.ipnet + act['logo_img']
			if not int(act['regis_cost']):act['regis_cost'] = '免费' 
			act['classify'] = act['classify'].split("|")[:int(options.classify_num_show)]
		return act_list