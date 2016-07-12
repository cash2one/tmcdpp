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
from wechausermodel import WechaUserModel

sys.path.append("..")
from Func.publicfunc import PublicFunc


class InterestModel(DbBase):
    def __init__(self):
        DbBase.__init__(self)
        self.table = 'fs_user_interest'


    def get_user_interest(self,uid):
        uid = str(uid)
        return self.db.query("SELECT i.iname from fs_user_interest AS ui LEFT JOIN fs_interest AS i ON ui.iid=i.iid WHERE ui.uid=" + uid)
      























    


