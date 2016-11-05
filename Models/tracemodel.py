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
class TraceModel(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.table = 'fs_trace'

    @classmethod
    def get_instance(cls):
        if not cls.model_instance: cls.model_instance = TraceModel()
        return cls.model_instance

    def save_trace(self,uid,logitude,latitude):
        current_time = PublicFunc.get_current_stamp()
        current_date = PublicFunc.get_current_datetime()
        result = self.insert_into_db({'uid':uid,'logitude':logitude,'latitude':latitude,'timestamp':current_time,'date_time':current_date})
        return 

        # if self.insert_into_db({'group_id':group_id,'uid':uid,'invitetime':PublicFunc.get_current_stamp()}): return True

    	

