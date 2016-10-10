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
from random import sample
import copy
import tornado.autoreload 
import operator
import socket
from tornado.options import define, options
import json
# import config
from connection import Connection

class DbBase:

    def __init__(self):
        self.db = Connection.get_connection_instance().db
        self.cache = Connection.get_connection_instance().cache
        self.table = None
    model_instance = None
    # def get_instance(cls):
    #     if not cls.model_instance : cls.model_instance = self()

    def insert_into_db(self,data_dict):
        key_str = ''
        value_str = ''
        for key in data_dict:
            key_str += key + ','
            data_dict[key] = ("%s" % data_dict[key])
            value_str += '"' + data_dict[key] + '"' + ','
        key_str = ' (' + key_str[:-1] + ') '
        value_str = ' (' +  value_str[:-1] + ') '
        sql = "INSERT INTO %s %s VALUES %s" % (self.table,key_str,value_str)
        try: 
            print sql
            result = self.db.execute(sql)
            return result
        except Exception,e: 
            print e
            raise

   
    def find_db_sum(self,**query_dict):
        """input dict and return the count of query """
        sql = "SELECT COUNT(*) AS sum FROM " + self.table + ' WHERE '
        for index in query_dict:
            if not isinstance(query_dict[index],dict): sql += " %s = '%s' and" % (index,query_dict[index]) 
            else:   sql += " %s %s '%s' and" % (index,query_dict[index]['rule'],query_dict[index]['value'])
        sql = sql[0:-3]
        print sql
        # self.out(sql)
        try: sum = self.db.get(sql)['sum']
        except Exception,e: 
            print e
            raise
        return int(sum) if int(sum) else 0

    def find_data(self,field_list,get_some=True,order=None,**query_dict):
        """ find one or more data from mysql"""
        start_sql = 'SELECT '
        sql = ''
        query_sql = ''
        for field in field_list: start_sql += field + ',' 
        start_sql = start_sql[0:-1] + ' FROM %s WHERE ' % (self.table)
        try:
            if query_dict:
                for index in query_dict:
                    if not isinstance(query_dict[index],dict): query_sql += " %s = '%s' and" % (index,query_dict[index]) 
                    elif query_dict[index]['rule'] == 'like':
                        query_sql += str(index)  + " like '%%" + query_dict[index]['value'] + "%%' and"
                    else: 
                        query_sql += " %s %s '%s' and" % (index,query_dict[index]['rule'],query_dict[index]['value'])
            sql = (start_sql + query_sql)[0:-3]   
            if order: sql= sql + ' order by ' + order
            if get_some is True: info_list = self.db.query(sql)
            elif get_some is False : 
                sql = sql + ' limit 1'
                info_list = self.db.get(sql)#only fetch one 
            elif isinstance(get_some,tuple):
                sql = sql + ' limit ' + str(get_some[0]) + ',' + str(get_some[1])
                info_list = self.db.query(sql)
            else:
                sql = sql + ' limit ' + str(get_some)
                info_list = self.db.query(sql)
            print sql
            return info_list
        except Exception,e: 
            print e     
            raise

    def update_db(self,change_param,update_type='reset',**where):
        """the change_param is dict  reset the db info and the default oper is reset and also have add but the add may + or -  """
        try:
            change_sql = "UPDATE %s SET" % (self.table)
            for key in change_param:
                if update_type == 'reset':
                    change_sql += " %s='%s'," % (key,change_param[key])
                elif update_type == 'add':
                    change_sql += " %s=%s+%s," % (key,key,change_param[key])
            change_sql = change_sql[0:-1] + ' WHERE'
            for key in where:
                change_sql += " %s='%s' and " % (key,where[key])
            change_sql = change_sql[0:-4]
            print change_sql
            # print change_sql
            self.db.execute(change_sql)
            return True
        except Exception,e: 
            print e
            raise


    def sql_update(self,sql):
        """
        you can update using your custom sql 
        """
        self.db.execute(sql)

    def sql_select(self,sql):
        return self.db.query(sql)




