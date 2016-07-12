#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import tornado.options
import tornado.web
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
# import config
from  pdatabase import DbBase
sys.path.append("..")
from Func.publicfunc import PublicFunc

class WechaUserModel(DbBase):
    
    def __init__(self):
        DbBase.__init__(self)
        self.table = 'fs_wecha_user'

    @classmethod
    def get_instance(cls):
    	if not cls.model_instance : cls.model_instance  = WechaUserModel()
    	return cls.model_instance

    def wecha_user_get(self,info_dict):
    	"""获取微信用户新，如果该微信用户不存在的话，创建该用户，并返回微信用户主键，如过存在的话娿，那么返回其在主用户表中的主键,and pk in wecha_user"""
        if not self.find_db_sum(unionid=info_dict['unionid']):
        	return 'create',self.insert_into_db(info_dict)
        else:
        	wecha_user_info = self.find_data(['uid','id'],get_some=False,unionid=info_dict['unionid'])
        	# return wecha_user_info
        	return 'exist',wecha_user_info['uid'],wecha_user_info['id']

    def bind_user_wecha_user(self,id,uid):
    	"""将主表uid 绑定到 微信用户表的数据中"""
        """ bind the user in main user table and wecha user table, the id is the pk of the fs_wecha_user """
        return self.update_db({'uid':uid},id=id)

    def judge_uid_in_wecha_user(self,uid):
    	"""判断用户主表中的uid是否在微信用户表中存在，"""
    	return self.find_db_sum(uid=uid)

    def judge_wecha_user_exist(self,unionid):
    	"""判断该微信用户是否存在,如果存在返回真"""
    	return True if self.find_db_sum(unionid=unionid) else False









