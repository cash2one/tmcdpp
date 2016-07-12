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


class UsersModel(DbBase):
    def __init__(self):
        DbBase.__init__(self)
        self.table = 'fs_users'
        self.user_import_param = ['token','avatar','tel','nickname','point','uid']

    @classmethod
    def get_instance(cls):
        if not cls.model_instance: cls.model_instance = UsersModel()
        return cls.model_instance

    def get_token(self,uid):#cast exception 
        uid = str(uid)
        self.cache_import_user_info(uid)
        return self.get_import_user_info(uid,['token'])['token']

    def check_token_available(self,uid,token_client): #cast exception 
        token_server = self.get_token(uid)
        return False if not token_server or not token_client == token_server else True

    def test(self):
        return PublicFunc.get_current_stamp()

    def clear_user_cache(self,uid):#cast exception 
        uid = str(uid)
        if self.cache.exists('users:uid:' + uid): self.cache.delete('users:uid:' + uid)  
        return True

    def get_normal_user_info(self,uid,param):
        return self.find_data(param,get_some=False,uid=uid)

    def judge_uid_exist(self,uid):
        uid = int(uid)
        return self.find_db_sum(uid=uid,status=0)

    def get_import_user_info(self,uid,param): #cast exception
        """if user login set the avatar token tel nickname info into cache"""
        uid = str(uid)
        self.cache_import_user_info(uid)
        info = self.cache.hmget('users:uid:' + uid,param)
        return_dict = {}
        for index,s_param in enumerate(param): return_dict[s_param] = info[index]  
        return return_dict
    
    def cache_import_user_info(self,uid): #cast exception
        uid = str(uid)
        if not self.cache.exists('users:uid:' + uid):
            user_info = self.find_data(self.user_import_param,get_some=False,uid=uid)
            user_info['avatar'] = options.ipnet + user_info['avatar']
            self.cache.hmset('users:uid:' + uid,user_info)
            self.cache.expire('users:uid:' + uid,options.user_info_expires)
        return True

    def check_tel_register(self,tel):
        """判断该手机号是否在用户表中存在"""
        return self.find_db_sum(tel=tel,status=0)

    def get_uid_via_tel(self,tel):
        user_info = self.find_data(['uid'],get_some=False,tel=tel,status=0)
        return user_info['uid'] if not user_info is None else None

    def login(self,tel,input_password):
        if not self.check_tel_register(tel):  return 0 #not register 
        return self.find_data(['password','uid','login_times','token'],get_some=False,tel=tel)

    def update_user_token(self,uid):
        """temp function """
        token = PublicFunc.create_token(uid)
        change_param = {'token':token}
        self.update_db(change_param,uid=uid)
        self.clear_user_cache(uid)
        self.cache_import_user_info(uid)
        return token

    def create_null_user(self):
        return self.insert_into_db({})

    def logout(self,uid):
        self.clear_user_cache(uid)
        self.update_db({'token':''},uid=uid)
        return True

    def judge_wecha_tel_bind(self,uid):
        """用于判断是否手机或者威信是否都绑定了,如果都绑定到话，返回真"""
        """return true if has  bind else false """
        tel =  self.find_data(['tel'],get_some=False,uid=uid)['tel']
        if not tel: return False 
        else: return WechaUserModel.get_instance().judge_uid_in_wecha_user(uid)
    
    def judge_tel_bind_status(self,tel):
        """判断手机号是 or not 绑定了其他账号,使用前提是该手机号码存在,返回为真表示该手机号已经被绑定了"""
        uid_in_users_table = self.get_uid_via_tel(tel)
        return  WechaUserModel.get_instance().judge_uid_in_wecha_user(uid_in_users_table)

    def get_accept_bind_show(self,uid):
        """judge wheather the user accept the layer show if return true means  accept"""
        return False if int(self.find_data(['show_bind'],get_some=False,uid=uid)['show_bind']) else True

    def judge_show_bind_layer(self,uid):
        """return true if we need show the layer """
        return True if not self.judge_wecha_tel_bind(uid) and self.get_accept_bind_show(uid) else False

    def refuse_show_bind_layer(self,uid):
        return self.update_db({'show_bind':1},uid=uid)

    def get_bind_info(self,uid):
        tel = self.find_data(['tel'],get_some=False,uid=uid)['tel']
        wecha_bind = WechaUserModel.get_instance().judge_uid_in_wecha_user(uid)
        tel_status = 1 if tel else 0 
        wecha_status = 1 if wecha_bind else 0 
        return {'tel':tel,'tel_status':tel_status,'wecha_status':wecha_status}
    
    def send_wecha_bind_tel_code(self,tel,uid):
        """向待绑定微信的手机号发送验证码 """
        if not PublicFunc.tel_regex(tel): return '手机号码不合法' #手机号码不合法
        if self.get_uid_via_tel(tel) is None: return '该手机号未注册！'#提醒用户去注册
        if self.judge_tel_bind_status(tel): return '该手机号已经被绑定'#该账号已经被绑定
        if self.cache.exists('bind:tel:' + tel): return '验证码已经发送' #验证码已经发送
        code = PublicFunc.get_random_num(4)
        content = '您要绑定手机号 验证码为' + code + ' 有效期为5分钟'
        PublicFunc.send_sms(tel,content)
        self.cache.set('bind:tel:' + tel,code)
        self.cache.expire('bind:tel:' + tel,options.bind_tel_expires)
        return True #验证码发送成功

    def delete_user_via_pk(self,uid):
        """软删除用户主表中数据根据主键"""
        return self.update_db({'status':1},uid=uid)

    def update_tel_in_cache(self,uid,tel):
        uid = str(uid)
        if self.cache.exists('users:uid:' + uid):
            self.cache.hset('users:uid:' + uid,'tel',tel)

    def find_friends(self,find_nick,page):
        """
         根据昵称找好友
        """
        friends_find_per_page = int(options.friends_find_per_page)
        page = int(page)
        friends_list = self.find_data(['uid','nickname','avatar'],get_some=(friends_find_per_page*page,friends_find_per_page),nickname={'rule':'like','value':str(find_nick)})
        return friends_list



    def treat_tel_bind(self,tel,code,uid):
        """
        (当然这里用户使用微信登录的时候才会有)如果微信要绑定手机号的话，那么需要传入手机号，验证码以及用户当前登录的uid，当然，既然要绑定手机号，那么这个手机号必然没有被绑定过
        由于用户当前是使用的微信登录之后获取到的uid 和 token，为了保证uid和token 可用，所以即使这个uid所对应的行当中tel为空也不能软删这条数据
        步骤:
        (1)手机号合法性判断
        (2)手机号是否已经被绑定判定
        (3)判断输入的uid所代表的微信号是否已经绑定手机号
        (4)判断验证码是否存在或者过期
        (5)判断验证码是否正确
        (6)注销old手机号账户
        (7)混合数据
        (8)重新绑定
        """
        if not PublicFunc.tel_regex(tel): return '手机号码不合法' #手机号码不合法
        if self.get_uid_via_tel(tel) is None: return '该手机号未注册！' #提醒用户去注册
        if self.judge_tel_bind_status(tel): return '该手机号码已经被绑定'#该手机号码已经被绑定
        if self.judge_wecha_tel_bind(uid): return '该微信号经被绑定'#该微信号经被绑定
        code_cache = self.cache.get('bind:tel:' + tel)
        if not code_cache: return '还没有获取验证码'#还没有获取验证码
        if not str(code) == code_cache: return '验证码错误'#验证码错误
        self.cache.delete('bind:tel:' + tel)
        ori_uid = self.get_uid_via_tel(tel)#绑定的手机号由于肯定是注册过的，获取uid 
        self.update_db({'status':1},tel=tel) #注销old手机号账户
        
        # print uid_in_users_table  #在这里可以混数据了   ==================================================================================
        self.update_db({'tel':tel},uid=uid)#修改用户主表来绑定手机号
        self.update_tel_in_cache(uid,tel)
        return True

    def get_wecha_bind_tel(self,uid):
        """判断某个微信号是否已经绑定了手机号，uid为微信用户表中所指向的主表的主键"""
        tel = self.find_data(['tel'],get_some=False,uid=uid)['tel']
        return tel if tel else False


    def send_admin_bind_code(self,tel):
        """管理员绑定时候发送验证吗"""
        tel = str(tel)
        if not PublicFunc.tel_regex(tel): return '手机号码不合法' #手机号码不合法
        #该手机号码已经被绑定 reuturn 1 
        if self.cache.exists('admin:bind:tel:' + tel): return '验证码已经发送' #验证码已经发送
        code = PublicFunc.get_random_num(4)
        content = '您要绑定手机号 验证码为' + code + ' 有效期为5分钟'
        self.cache.set('admin:bind:tel:' + tel,code)
        self.cache.expire('admin:bind:tel:' + tel,options.bind_tel_expires)
        if not PublicFunc.send_sms(tel,content): return '发送失败'
        return True

    def treat_admin_bind_code(self,tel,code):
        """处理管理员绑定时候的验证吗 还没有写好"""
        tel = str(tel)
        if not PublicFunc.tel_regex(tel): return '手机号码不合法' #手机号码不合法
        #该手机号码已经被绑定 reuturn 1 
        code_cache = self.cache.get('admin:bind:tel' + tel)
        if not code_cache: return '验证码失效，请重新发送'
        if not code == code_cache: return '验证码错误'

    def change_user_point(self,uid,num):
        """修该用户积分数num为修改到数目，可以为负数"""
        uid = str(uid)
        self.update_db({'point':num},update_type='add',uid=uid)
        if self.cache.exists('users:uid:' + uid):
            self.cache.hincrby('users:uid:' + uid,'point',num)
        return True

    def make_false_user_data(self):
        tel_base = 20000000001
        tel = tel_base + 1 
        for i in xrange(0,99): 
            tel = tel_base + i
            self.insert_into_db({'tel':tel,'password':'111111'})
        
    def get_double_user_info(self):
        rn = random.randint(0,3000)
        return self.find_data(['nickname','avatar','uid'],status=0,get_some=(rn,2))
        


































    


