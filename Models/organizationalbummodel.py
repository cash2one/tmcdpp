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

class OrganizationAlbumModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'organization_album'


	def get_album_list(self,organization_id,page):
		"""
		"""
		per_page = 5 
		jump = int(per_page) * int(page)
		return self.find_data(['*'],get_some=(jump,per_page),organization_id=organization_id,order=" create_time desc ")



		# create_album(uid,org_id,album_name)
	def create_album(self,uid,org_id,album_name):
		data_dict = {'organization_id':org_id,'name':album_name,'create_time':PublicFunc.get_current_datetime(),'count':0,'show_times':0,'msg':'','create_user':uid}
		va = self.insert_into_db(data_dict)
		return va 

	def get_album_info(self,album_id):
		return self.find_data(['*'],get_some=False,id=album_id) 

