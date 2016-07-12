#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import re
import redis
import time
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
from pmongo import MongoBase
from Func.publicfunc import PublicFunc
from usersmodel import UsersModel

class MongoTestModel(MongoBase):
	def __init__(self):
	    MongoBase.__init__(self)
	    self.m_c = self.mongo_db.test


    # def set_index(self):
    	# self.m_c.ensureIndex()


    

	def add(self):
	    info = {'dou':1411,'info_list':[]}
	    self.m_c.insert(info)
	    num_str = "01023001452"
	    for i in xrange(0,5):
	    	random = ''.join(sample(num_str,3))
	    

	def adding(self):
		self.m_c.update({'dou':1411},{"$push":{'info_list':{"$each":[{'num':438},{'num':437}],"$sort":{'num':1}}}})

	@classmethod 
	def get_instance(cls):
		if not cls.model_instance:cls.model_instance = MongoTestModel()
		return cls.model_instance
