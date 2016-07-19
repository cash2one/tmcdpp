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
from groupmodel import GroupModel

class UserEventModel(DbBase):

    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_user_event'


    @classmethod 
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = UserEventModel()
    	return cls.model_instance

	def save_attend_info(self,**attend_info):
		"""保存报名信息"""
		return self.insert_into_db(attend_info)

    def set_user_comm(self,uid,gid,comm_id):
        """设置用户所在协会"""
        self.update({"comm_id":comm_id},uid=uid)

    def check_have_attend_game(self,uid,gid):
        """
        根据赛事id来判断用户是否参加了赛事
        """
        return self.find_db_sum(uid=uid,gid=gid,status=0)

    def check_have_attend_comm(self,uid,gid):
        """
        function :判断用户是否加入跑团,这个函数目前针对类似北京线上健步走这种赛事
        author: 殷帅
        input param: 
             uid:  用户id  
             gid:  赛事id
        return param:
             如果用户都没有报名的话，那么返回None
             用户已经报名赛事但是没有加入跑团，返回False,报名主键
             用户已经报名赛事同样加入了跑团，返回True,跑团主键
        """
        attend_info = self.find_data(['ueid','comm_id'],get_some=False,uid=uid,gid=gid,status=0)
        if  attend_info is None: return None
        else:
            if attend_info['comm_id']: return True,attend_info['comm_id']
            else: return False,attend_info['ueid']


    def attend_comm(self,comm_id,id):
        """修改用户报名表中用户所加入的跑团，其中id为报名表主键"""
        self.update_db({"comm_id":comm_id},ueid=id)
        return True

    def get_all_attend_man(self,eid):
        return self.find_data(['uid'],eid=eid,status=0)

    def check_attend_type(self,uid,eid):
        """
        判断用户报名方式，是团队报名还是个人报名
          this method used as (1)judge if user has attend the event (2)if user has attend the event,then judge the attend type(group or personal)
        if the user has not attend,then return false, if the user has attend and the attend type is group,then return the group_id else return 0 
        """
        attend_info = self.find_data(['group_id'],get_some=False,status=0,uid=uid,eid=eid)
        if attend_info is None: return False
        return attend_info['group_id']


    # def judge_attend_type(self,uid,eid):
    #     """
    #     this method used as (1)judge if user has attend the event (2)if user has attend the event,then judge the attend type(group or personal)
    #     if the user has not attend,then return false, if the user has attend and the attend type is group,then return the group_id else return 0 
    #     """
    #     return int(self.find_one('fs_user_event',['group_id'],uid=uid,status=0,eid=eid)['group_id'])
