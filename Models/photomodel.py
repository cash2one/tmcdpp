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

class PhotoModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'photo'
		self.org_pic = 1101
		self.file_path = "/var/www/html/Uploads/AlbumPic/"


	def add_pic(self,uid,album_id,file_name,org_id):
		create_time = int(time.time())
		type = self.org_pic
		web_path = options.ipnet + "/Uploads/AlbumPic/" + file_name
		self.insert_into_db({'user_id':uid,'create_time':create_time,'type':type,'type_id':org_id,'target_id':album_id,'file_path':'','web_path':web_path,
							'file_name':file_name,'file_path':self.file_path,'file_old_name':'','old_width':0,'old_height':0,'old_size':0,
							'msg':''})
		return 

	def get_album_pic_list(self,organization_id,album_id,last_id,max_get):
		if not last_id:
			last_id = self.db.get("select max(id) as max from photo")['max'] + 1
		pic_list = self.find_data(['create_time','file_name','id'],type_id=organization_id,target_id=album_id,id={'rule':'<','value':last_id},get_some=(0,max_get),order=" id desc ")
		return pic_list



