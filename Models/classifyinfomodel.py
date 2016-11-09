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
from Func.publicfunc import PublicFunc
from usersmodel import UsersModel
from  pdatabase import DbBase

class ClassifyInfoModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'classify_info'


	def get_classname_by_code(self,code):
		"""
		"""
		classname = self.find_data(['id','name'],get_some=False,code=code)
		return classname

	@classmethod
	def get_instance(cls):
		if not cls.model_instance:cls.model_instance = ClassifyInfoModel()
		return cls.model_instance

