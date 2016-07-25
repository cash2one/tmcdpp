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


class GroupModel(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_group'

    @classmethod
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = GroupModel()
    	return cls.model_instance

    def cache_group_info(self,group_id):
    	group_id = str(group_id)
    	if not self.cache.exists('group:id:' + group_id) and self.judge_group_exist(group_id):
    		group_info = self.find_data(['*'],get_some=False,id=group_id)
    		group_info['createtime'] = PublicFunc.stamp_to_YmdHM(group_info['createtime'])
    		group_info['tag_name'] = TagModel.get_instance().get_tag_name(group_info['tag_id'])
    		group_info['avatar'] = options.ipnet + str(group_info['avatar'])
    		self.cache.hmset('group:id:' + group_id,group_info) #write into cache
        	self.cache.expire('group:id:' + group_id,options.group_info_expires)

    def get_group_info(self,group_id,param_list=None):
    	self.cache_group_info(group_id)
    	group_info = self.cache.hgetall('group:id:' + str(group_id))
    	group_info_return = {}
    	if not param_list: return group_info
        else:
        	for value in param_list:
        		group_info_return[value] = group_info[value]
        	return group_info_return

    def delete_group(self,group_id):
    	self.__delete_group_from_db(group_id)
    	self.__delete_group_from_cache(group_id)
    	# GroupMemModel.get_instance().truncate_group_mem(group_id)   ############################################################
    	return True

    def __delete_group_from_db(self,group_id):
        return self.update_db({'status':1},id=group_id)

    def __delete_group_from_cache(self,group_id):
    	group_id = str(group_id)
    	if self.cache.exists('group:id:' + group_id): 
    		self.cache.delete('group:id:' + group_id)

    def __change_group_info_cache(self,group_id,change_param):		
    	"""更新缓存中团队到信息"""
    	group_id = str(group_id)
        if self.cache.exists('group:id:' + group_id):
        	self.cache.hmset('group:id:' + group_id,change_param)
        return True

    def __change_group_info_db(self,group_id,change_param):
        """更新db中团队到信息"""
        return self.update_db(change_param,id=group_id)

    def change_group_info(self,group_id,**change_param):
    	self.__change_group_info_db(group_id,change_param)
    	self.__change_group_info_cache(group_id,change_param)
    	return True

    def check_is_leader(self,uid,group_id):
        leader_id = self.get_group_info(group_id,['leader_id'])['leader_id']
        return True if int(uid) == int(leader_id) else False


    def change_group_mem_num(self,group_id,change_num):
        """改变团队人数"""
    	membernum = self.get_group_info(group_id,['membernum'])['membernum']
    	new_membernum = int(membernum) + change_num
    	self.__change_group_info_db(group_id,{'membernum':new_membernum})
    	self.__change_group_info_cache(group_id,{'membernum':new_membernum})
    	return True

    def get_group_num(self,uid):
        """
        获取团队总数 
        """
        uid = int(uid)
        return self.find_db_sum(leader_id=uid,status=0)

    def get_some_group(self,uid,get_num):
        """
        获取指定数目的团队
        """
        return self.find_data(['group_name','avatar','id as group_id'],get_some=get_num,order=' createtime desc ',leader_id=uid,status=0)

    def judge_group_exist(self,group_id):
        return self.find_db_sum(id=group_id,status=0)























 #     if not self.cacheRedis.exists('mygroup:uid:' + uid):
         #        group_id_list_db = self.db.query("SELECT group_id FROM fs_group_mem  WHERE uid = %s and is_leader=0",uid)
         #        for value in group_id_list_db:
         #            self.cacheRedis.lpush('mygroup:uid:' + uid,value['group_id'])
         #     group_id_list = self.cacheRedis.lrange('mygroup:uid:' + uid,0,-1) 
         #     for group_id in group_id_list:
         #         group_info_return.append(self.get_group_info(group_id))
         #     if not self.cacheRedis.exists('leadergroup:uid:' + uid):
         #         group_id_list_db = self.db.query("SELECT group_id FROM fs_group_mem  WHERE uid = %s and is_leader=1",uid)
         #         for value in group_id_list_db:
         #             self.cacheRedis.lpush('leadergroup:uid:' + uid,value['group_id'])   
         #     leader_group_id_list = self.cacheRedis.lrange('leadergroup:uid:' + uid,0,-1)
         #     for group_id in leader_group_id_list:

    def __get_group_user_info_via_uid_list(self,uid_list):
		group_user_info_list = []
		for uid in uid_list:
			group_user_info_list.append(UsersModel.get_instance().get_import_user_info(uid,['avatar','point','nickname','uid']))
		return group_user_info_list











