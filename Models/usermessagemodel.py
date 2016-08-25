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

class UserMessageModel(DbBase):
	def __init__(self):
		DbBase.__init__(self)
		self.table = 'user_message'

	def save_message_info(self,type,target_id,title,content,target_img,target_url):
		self.insert_into_db(type=type,target_id=target_id,title=title,content=content,target_img=target_img,target_url=target_url)
		return 



