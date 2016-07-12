#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
import time
from random import sample
import hashlib
import operator
from functools import wraps
import urllib2
import urllib
import re 
from datetime import date

class PublicFunc:
    
    @staticmethod
    def stamp_to_YmdHM(stamp):    
		return time.strftime("%Y-%m-%d %H:%M",time.localtime(int(stamp))) 

    @staticmethod
    def stamp_to_Ymd(stamp):
        return time.strftime("%Y-%m-%d",time.localtime(int(stamp))) 


    @staticmethod
    def get_current_stamp():
		return int(time.time())

    @staticmethod
    def create_token(uid):
        """ the access_token is 10 random str + uid + current time and then do md5 secret"""
        token_str = PublicFunc.get_random(5) + str(uid) + str(int(time.time()))
        m = hashlib.md5()
        m.update(token_str)
        return m.hexdigest()
     
    @staticmethod
    def get_random(num):
        """get num random str"""
        return  ''.join(sample('abcdefghijklmnopqrstuvwxyz1234567890!',num))

    @staticmethod    
    def add_rank_string(input_list):
        for index,value in enumerate(input_list):
    		input_list[index]['rank_string'] = '第' + str(index + 1) + '名'
    	return input_list

    @staticmethod
    def send_sms(tel,content):
        url = 'http://101.200.214.68/index.php/Api/Users/sendSmsCode/tel/' + tel + '/content/' + content
        return urllib2.urlopen(url).read()

    @staticmethod
    def do_curl_get(url): 
        """python 做get请求 """
        return urllib2.urlopen(url).read()

    @staticmethod
    def get_random_num(num):
        return ''.join(sample('0123456789',num))

    @staticmethod 
    def tel_regex(tel):
        # tel_compile = re.compile('^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}')
        tel_compile = re.compile('^(13[0-9]|14[0-9]|15[0-9]|18[0-9]|17[0-9])\d{8}')
        return True if tel_compile.match(tel) else False 

    @staticmethod
    def get_akt_content(content):
        """
          正则匹配，例如在新浪微博中，  when match chinese ,you should use u before 
        """
        r = re.compile(ur"@([\u4E00-\u9FA5\w-]+)")
        return r.findall(content)

    @staticmethod
    def time_format_span(timestamp,current_time): 
        """时间戳转换为1分钟之前 刚刚 这种东西"""
        timestamp = int(timestamp)
        current_time = int(current_time)
        differ =  current_time  - timestamp
        if differ < 60 : return '刚刚'
        elif differ < 3600: return str(differ/60) + '分钟前'
        elif differ < 43200: return str(differ/3600) + '小时前'
        else: return PublicFunc.stamp_to_Ymd(timestamp)

    @staticmethod
    def get_age_via_idcard(idcard):
        bir_year = int(idcard[6:10])
        now_year = int(time.strftime("%Y",time.localtime()))
        age =  now_year - bir_year
        return age if age > 0 else 0

    @staticmethod
    def get_some_char(str,fetch_num):
        """
        function: 主要用于对一个中英文字符串取出其中的部分，但是又不破坏中文的构成，适合编码utf8

        """
        pass

    @staticmethod
    def get_date_info(timestamp,param):
        reflect_dict = {"year":0,'month':1,'day':2}
        date_tuple = time.localtime(timestamp)
        info_return = {} 
        for p in param:
            info_return[p] = date_tuple[reflect_dict[p]]
        return info_return

    @staticmethod
    def get_date_today():
        return str(date.today())










        


