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
class OrganizationApplyModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'organization_apply'

	def save_apply_info(self,apply_info):
		"""

		"""
		self.insert_into_db(apply_info)
		return 