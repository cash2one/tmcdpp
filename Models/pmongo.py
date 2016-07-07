#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import re
import redis
import time
import tornado.auth
import tornado.options
import unicodedata
import sys
import random
import hashlib
import requests
from random import sample
import copy
import operator
import socket
from tornado.options import define, options
import json
import config
from pymongo import MongoClient
from connection import Connection

class MongoBase:

    def __init__(self):
		# self.mongo_client = pymongo.Connection('localhost',27017)
		self.mongo_client = MongoClient("101.200.214.68") #default localhost 27017 
		# self.mongo_client = MongoClient()
		self.mongo_db = self.mongo_client.fitness
		self.m_c = None
		self.cache = Connection.get_connection_instance().cache

    model_instance = None

    # def push_subdoc(self,keyname,push_data_list,sort_field,sort_way='asc',**query):
    #     """ 
    #         function : 该函数用于向子文档中添加字典数据
    #         param: 
    #             keyname: 待插入数据的子文档的key
    #             push_data_list: 插入的数据，格式为列表，列表当中为字典数据
    #             sort_way: asc 为升序  des 为降序
    #             query: 查询字典
    #         asc shengxu  des jiangxu   
    #     """


