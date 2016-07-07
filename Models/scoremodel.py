#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import os.path
import re
import redis
import time
import tornado.database
import sys
import copy
import operator
import socket
from tornado.options import define, options
import json
import config
from  pdatabase import DbBase
from Func.publicfunc import PublicFunc
from tagmodel import TagModel
from usersmodel import UsersModel

class ScoreModel(DbBase):
    def __init__(self):
    	DbBase.__init__(self)
    	self.table = 'fs_scores'

    def get_score_list(self,gid):
    	"""根据赛事id 获取成绩播报列表列表"""
    	score_list =  self.find_data(['*'],order='time desc',gid=gid,status=0)
    	for index,score in enumerate(score_list):
    		score_list[index]['pic'] = options.ipnet + score['pic']
    		score_list[index]['time'] = PublicFunc.stamp_to_YmdHM(score['time'])
        return score_list
        
    @classmethod
    def get_instance(cls):
    	if not cls.model_instance: cls.model_instance = ScoreModel()
    	return cls.model_instance

