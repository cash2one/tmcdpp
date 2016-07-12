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
import tornado.web
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
from usersmodel import UsersModel

class Combine(DbBase):
    def __init__(self):
	    DbBase.__init__(self)
	    self.usersmodel = UsersModel.get_instance()

	def test(self):
		print self.usersmodel
	