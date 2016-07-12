#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import sys
import random
import hashlib
import requests
import urllib2
import urllib
from random import sample
import copy
import tornado.autoreload 
import operator
import socket
from tornado.options import define, options
import json
import config
from Models.usersmodel import UsersModel
from Models.musermodel import MUserModel
from Models.runcommunitymodel import RunCommunityModel
from Func.publicfunc import PublicFunc
# from Func.publicfunc import PublicFunc
from bson.objectid import ObjectId

class RCommController:
	usersmodel = UsersModel()
	runcommunitymodel = RunCommunityModel()

	def save_run_data(self,uid,duration,distance):
		self.runcommunitymodel.save_run_data(uid,duration,distance)
		