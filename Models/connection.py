#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import tornado.web
import unicodedata
import sys
import random
import hashlib
import requests
from random import sample
import socket
from tornado.options import define, options
import json
# import config

class Connection:
    def __init__(self):
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)
        self.cache = redis.Redis(host=options.redis_host,port=options.redis_port,db=options.redis_db)
    connection_instance = None
    @classmethod
    def get_connection_instance(cls):
        if not cls.connection_instance: cls.connection_instance = Connection()
        return cls.connection_instance
