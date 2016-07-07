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
from groupmodel import * 

class InviteModel(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_invite'

    def judge_alreay_send_invite(self,uid,group_id):
        return True if self.find_db_sum(group_id=group_id,uid=uid)  else False

    def write_group_invite(self,uid,group_id):
        if self.insert_into_db({'group_id':group_id,'uid':uid,'invitetime':PublicFunc.get_current_stamp()}): return True

    def get_invite_info(self,id):
        return self.find_data(['uid','group_id'],get_some=False,id=id)

    def get_group_invite_list(self,uid): 
        invite_list = self.find_data(['group_id','id'],status=0,uid=uid)
        invite_info_return = []
        for invite_info in invite_list:
            invite_group_info = GroupModel.get_instance().get_group_info(invite_info['group_id'])
            invite_group_info['invite_id'] = invite_info['id']
            invite_info_return.append(invite_group_info)
        return invite_info_return

    def delete_invite(self,invite_id): 
        self.update_db({'status':1},id=invite_id)

        

    
    	

