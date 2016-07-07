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
import config
from  pdatabase import DbBase

sys.path.append("..")
from Func.publicfunc import PublicFunc

class SystemModel(DbBase):
    def __init__(self):
		DbBase.__init__(self)
		self.table = 'fs_sysinfo'

    @classmethod
    def get_instance(cls):
        if not cls.model_instance: cls.model_instance = SystemModel()
        return cls.model_instance

    def get_sysinfo(self,uid):
	    info_list = self.find_data(['*'],order='id desc',uid=uid)
	    for index,info in enumerate(info_list):
			info_list[index]['time'] = PublicFunc.stamp_to_YmdHM(info['time']) 
	    return info_list
	    
    def del_sysinfo(self,id):
		if self.update_db({'status':1},id=id): return True
