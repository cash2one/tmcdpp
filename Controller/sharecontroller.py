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
from Models.notemodel import NoteModel
from Models.notecommodel import NoteComModel
from Models.postmodel import PostModel
from Models.postcommodel import PostComModel
from Func.publicfunc import PublicFunc
# from Func.publicfunc import PublicFunc
from bson.objectid import ObjectId

class ShareController:
	def __init__(self):
		self.share_title = options.share_title

	def share_post(self,post_id):
		post_info = PostModel().get_post_info(post_id)
		share_url = options.ipnet + '/ky/postpub?action=get_post_info&uid=0&version=3.2&post_id=' + post_id
		share_dict = {'title':self.share_title,'content':post_info['content'],'image':options.ipnet + post_info['pic_list'][0],'url':share_url}
		return share_dict

	def share_note(self,note_id):
		note_info = NoteModel().get_note_info(note_id)
		share_url = 'http://www.baidu.com'
		share_dict = {'title':self.share_title,'content':note_info['title'],'image':'not have','url':share_url}
		return share_dict
