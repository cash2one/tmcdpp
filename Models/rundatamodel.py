#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import sys
import copy
import operator
import socket
from tornado.options import define, options
import json
import config
from  pdatabase import DbBase
from Func.publicfunc import PublicFunc
from tagmodel import TagModel
from usersmodel import UsersModel
from groupmemmodel import GroupMemModel
from gamemodel import GameModel

class RunDataModel(DbBase):
    def __init__(self):
		DbBase.__init__(self)
		self.table = 'fs_rundata'

    @classmethod
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = RunDataModel()
    	return cls.model_instance

    def get_recent_run_man_single(self,eid):
    	"""获取最近运动的用户 针对于仅仅有一个项目的"""
    	recent_man_list = []
    	show_num = 6 
    	jump = 0 
    	while len(recent_man_list) < show_num:
    		user_run_list = self.find_data(['uid','step_count'],get_some=(jump,show_num),order=' id desc ',status=0)
    		if not user_run_list: break
    		jump += show_num
    		for user_run in user_run_list:
    			user_info = UsersModel.get_instance().get_import_user_info(user_run['uid'],['avatar','username'])
    			user_run['nickname'] = user_info['nickname'] if user_info['nickname'] else '小跑男'
    			user_run['avatar'] = user_info['avatar']
    			recent_man_list.append(user_run)
    			if len(recent_man_list) == show_num: break
    		if len(recent_man_list) == show_num: break
    	return recent_man_list






# hile len(recent_man_list) < show_num:
#                     user_list = self.db.query("SELECT uid,step_count AS step FROM fs_rundata WHERE status=0 order by id desc limit %s,%s",jump,jump+5)
#                     if not user_list: break
#                     jump = jump + 5
#                     for user_info in user_list:
#                         print self.check_have_attend_by_uid(user_info['uid'],eid)
#                         if  user_info not in recent_man_list and self.check_have_attend_by_uid(user_info['uid'],eid):
#                             recent_man_list.append(user_info)
#                             if len(recent_man_list) == show_num: break
#                 self.cacheRedis.set("recent_run_man:eid:" + eid,recent_man_list,options.recent_run_man)   









		