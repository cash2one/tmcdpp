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
from groupmodel import GroupModel

class GroupMemModel(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_group_mem'

    @classmethod
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = GroupMemModel()
    	return cls.model_instance

    def judge_alreay_in_group(self,uid,group_id):
        return True if self.find_db_sum(group_id=group_id,uid=uid,status=0) else False

    def add_mem_to_group(self,uid,group_id,is_leader=0):
    	return True if  self.insert_into_db({'is_leader':is_leader,'group_id':group_id,'uid':uid,'attendtime':PublicFunc.get_current_stamp()}) else False

    def change_group_user_list_cache(self,group_id,uid):
    	group_id = str(group_id)
    	uid = str(uid)
    	if self.cache.exists('group_user_list:group_id:' + group_id):
    		self.cache.rpush('group_user_list:group_id:' + uid,group_id)

    def change_group_mem_num_cache(self,group_id,incr_num):
    	group_id = str(group_id)
        if self.cacheRedis.exists('group:id:' + group_id): 
            self.cache.hincrby('group:id:' + group_id,'membernum',incr_num)

    def __cache_group_user_list(self,group_id):
        """   缓存团队用户uid列表  """
        group_id = str(group_id)
        if not self.cache.exists('group_user_list:group_id:' + group_id):
	        group_user_list = self.find_data(['uid'],group_id=group_id)
	        for user_dict in group_user_list: self.cache.lpush('group_user_list:group_id:' + group_id,user_dict['uid'])
	        self.cache.expire('group_user_list:group_id:' + group_id,options.group_user_list_expires)

    def get_group_user_point_rank(self,group_id,get_num='all'):
        """获取用户积分排名信息，包含了用户的重要信息"""
        group_user_list = self.get_group_user_list(group_id,-1) #取出团队所有成员
        group_user_info_list = self.__get_group_user_info_via_uid_list(group_user_list)
        rank_user_info_list = sorted(group_user_info_list,key=operator.itemgetter('point'),reverse=True)
        if not get_num == 'all': rank_user_info_list = rank_user_info_list[:get_num]
        return PublicFunc.add_rank_string(rank_user_info_list)

    def get_group_user_list(self,group_id,get_num):
        """获取指定团队,指定数目的的用户uid 列表，按照加入顺序"""
    	group_id = str(group_id)
    	self.__cache_group_user_list(group_id)
    	return self.cache.lrange('group_user_list:group_id:' + group_id,0,get_num)

    def get_group_user_info_list(self,group_id,get_num):
        """获取指定团队,指定数目的的用户重要信息列表，按照加入顺序"""
    	group_user_list = self.get_group_user_list(group_id,get_num)
    	return self.__get_group_user_info_via_uid_list(group_user_list)

    def __get_group_user_info_via_uid_list(self,uid_list):
    	info_return = [] 
    	for uid in uid_list:
    		info_return.append(UsersModel.get_instance().get_import_user_info(uid,['username','point','uid','avatar'])) 
    	return info_return

    def get_my_group_list(self,uid):
        group_id_list_db = self.find_data(['group_id','is_leader'],uid=uid)
        my_group_leader = []
        my_group_not_leader = []
        for info in group_id_list_db:
            if int(info['is_leader']): my_group_leader.append(GroupModel.get_instance().get_group_info(info['group_id']))
            else: my_group_not_leader.append(GroupModel.get_instance().get_group_info(info['group_id'])) 
        return my_group_leader,my_group_not_leader

    def truncate_group_mem(self,group_id):
        self.update_db({'status':1},group_id=group_id)
        if self.cache.exists('group_user_list:group_id:' + group_id):
            self.cache.delete('group_user_list:group_id:' + group_id)
        return True

    def delete_group_mem(self,group_id,uid):
        """删除团队成员"""
        self.__delete_group_mem_db(group_id,uid)
        self.__delete_group_mem_cache(group_id,uid)
        return True

    def __delete_group_mem_cache(self,group_id,uid):
    	"""从cache中删除团队成员"""
    	group_id = str(group_id)
        if self.cache.exists('group_user_list:group_id:' + group_id):
            self.cache.lrem('group_user_list:group_id:' + group_id,uid)
        return True

    def __delete_group_mem_db(self,group_id,uid):
    	"""从db中删除团队成员"""
        return self.update_db({'status':1},group_id=group_id,uid=uid)


    def add_user_to_group(self,uid,group_id):
    	self.insert_into_db({'group_id':group_id,'uid':uid,'attendtime':PublicFunc.get_current_stamp()})
        GroupModel.get_instance().change_group_mem_num(group_id,1)
        



