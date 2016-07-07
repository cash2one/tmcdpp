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
from bson.objectid import ObjectId
"""
collection: cmember
name: 跑团成员集合
structure:


_id 主键,和跑团主键一致
 uid 成员用户id
 attend_time 成员加入时间 
 distance 成员运动距离(m)
 duration 成员运动时长(s)
 status  用户状态



"""