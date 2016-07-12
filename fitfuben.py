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
import config
from pdatabase import Test
reload(sys)
sys.setdefaultencoding('utf8')
settings = {'debug':True}
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/[pk]y/tag", TagHandler),
            (r"/base",BaseHandler),
            (r"/[pk]y/test",TestHandler),
            (r"/[pk]y/group",GroupHandler), 
            (r"/[pk]y/invite",InviteHandler),
            (r"/[pk]y/apply",ApplyHandler),
            (r"/[pk]y/attend",AttendHandler),
            (r"/[pk]y/game",GameHandler),
            (r"/[pk]y/gamemore",GamemoreHandler),
            (r"/[pk]y/rank",RankHandler),
            (r"/[pk]y/login",LoginHandler),
            (r"/[pk]y/logout",LogoutHandler),
            (r"/[pk]y/score",ScoreHandler),
            (r"/[pk]y/user",UserHandler),
            (r"/[pk]y/org",OrgHandler),
            (r"/[pk]y/point",PointHandler),
            (r"/[pk]y/system",SystemHandler),
            (r"/[pk]y/notify",NotifyHandler),
            (r"/[pk]y/sn",SnHandler),
            (r"/[pk]y/map",MapHandler),
            (r"/[p]y/pointbonus",PointbonusHandler),
            (r"/[py]y/science",ScienceHandler),
        ]
        settings = dict(
            blog_title=u"Tornado Blog",
            #dirname use to get the file path,join means combine 
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,###close this to aviod transfer xsvf to the register 
            #cookie_secret is signed to avoid 
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            debug = True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        self.cacheRedis = redis.Redis(host=options.redis_host,port=options.redis_port,
                                db=options.redis_db)
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    @property
    def cacheRedis(self):
        return self.application.cacheRedis

    def get_current_timestamp(self): 
        return int(time.time()) 

    def treat_ar_dict(self,input_dict,key_list,**other_param):
        dict_temp = copy.deepcopy(input_dict)
        for dict_key in key_list: 
            if dict_temp.has_key(dict_key): del dict_temp[dict_key] 
        return dict(dict_temp,**other_param)

    def get_attend_info(self,id):
        return self.find_one("fs_user_event",['*'],ueid=id)
    
    def get_group_attend_mem(self,id):
        """the func will return all ueid of the same attendtime """
        attend_info = self.get_attend_info(id)
        group_id = attend_info['group_id']
        attendtime = attend_info['attendtime']
        eid = attend_info['eid']
        try:
            ueid_list_db = self.db.query("SELECT ueid FROM fs_user_event WHERE group_id=%s and attendtime=%s and eid=%s",group_id,attendtime,eid)
        except:
            return False
        ueid_list = []
        for ueid_info in ueid_list_db:
            ueid_list.append(str(ueid_info['ueid']))
        return ueid_list

    def create_out_trade_num(self): #the out_trade_num is 20
        str_all = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        str_head = time.strftime("%y%m%d%H%M%S",time.localtime(int(time.time())))
        sn_tail = ''.join(sample(str_all,7))
        return str_head + sn_tail

    def check_token_available(self,uid,token_client):
        token_server = self.get_token(uid)
        if not token_server or not token_client == token_server : return self.return_param(0,502,{},'wrong token')
        return True

    def get_multi_argument(self,argument_list):
        """ input a list of argument and it will result a list of dict"""
        dict_return = {}
        for param in argument_list: 
            try:
                if isinstance(param,dict):
                    for key in param: 
                        if param[key] is False :
                            try: dict_return[key] = self.get_argument(key)
                            except:continue
                        else: dict_return[param] = self.get_argument(key,param[key])
                else: dict_return[param] = self.get_argument(param)
            except Exception,e: self.treat_except(e)
        return dict_return

    #add user into the group  insert uid into fs_group_mem 
    def add_user_to_group(self,uid,group_id):
        uid = str(uid)
        group_id = str(group_id)
        self.insert_into_db('fs_group_mem',{'group_id':group_id,'uid':uid,'attendtime':int(time.time())})
        self.update_db('fs_group',{'membernum':1},{'id':group_id},'add')
        if self.cacheRedis.exists('group_user_list:group_id:' + group_id): self.cacheRedis.rpush('group_user_list:group_id:' + group_id,uid)
        if self.cacheRedis.exists('mygroup:uid:' + uid): self.cacheRedis.lpush('mygroup:uid:' + uid,group_id)
        if self.cacheRedis.exists('group:id:' + group_id):  self.cacheRedis.hincrby('group:id:' + group_id,'membernum',1)
        return True

    def create_token(self,uid):
        """ the access_token is 10 random str + uid + current time and then do md5 secret"""
        token_str = self.get_random(5) + str(uid) + str(int(time.time()))
        m = hashlib.md5()
        m.update(token_str)
        return m.hexdigest()

    def clear_token(self,uid):
        pass


    def judge_attend_type(self,uid,eid):
        """
        this method used as (1)judge if user has attend the event (2)if user has attend the event,then judge the attend type(group or personal)
        if the user has not attend,then return false, if the user has attend and the attend type is group,then return the group_id else return 0 
        """
        return int(self.find_one('fs_user_event',['group_id'],uid=uid,status=0,eid=eid)['group_id'])

    def get_random(self,num):
        """get num random str"""
        return  ''.join(sample('abcdefghijklmnopqrstuvwxyz1234567890!',8))

    def treat_except(self,e):
        is_debug = options.is_debug
        if is_debug: self.return_param(0,505,{},str(e)) 
        else: raise tornado.web.HTTPError(500, "系统开小差了，请重新刷新")

    def judge_today_have_login(self,uid): 
        """  you wenti """
        early_night_timestamp =  self.get_early_night_timestamp()
        user_info = self.get_userinfo_via_search_param(['last_login'],uid)
        self.out(user_info)
        return True if user_info['last_login'] >= early_night_timestamp else False
    
    def get_point_info(self,id):
        """ get point info via db and redis """
        id = str(id)
        if not self.cacheRedis.exists("point_info:id:" + id):
            point_info = self.db.get("SELECT * FROM fs_point WHERE id=%s and status=0",id)
            self.cacheRedis.hmset('point_info:id:' + id,point_info)
        point_info = self.cacheRedis.hgetall('point_info:id:' + id)
        return point_info

    def give_point(self,uid,point_num):
        """ the point_num may have - and + """
        uid = str(uid)
        if self.cacheRedis.exists('users:uid:' + uid):
            self.cacheRedis.hincrby('users:uid:' + uid,'point',point_num)
        self.update_db('fs_users',{'point':point_num},{'uid':uid},'add') 
        if self.cacheRedis.exists("users:uid:" + uid):
            self.cacheRedis.hincrby("users:uid:" + uid,'point',point_num)

    def give_point_and_write_point_from_send_sysinfo(self,uid,pid,gid,point_num=False):
        self.give_point(uid,point_num)
        self.write_user_point_from(uid,pid,gid,point_num)

    def write_user_point_from(self,uid,pid,gid,point_num=False):
        """ write user_point_from,the default point_num is False,which means that the point of this kind of point is fixed 
            and if it is fixed,it will read point num from fs_point
        """
        write_data = {'pid':pid,'uid':uid,'gid':gid,'time':int(time.time())}
        if point_num: write_data['point_num'] = point_num 
        else: write_data['point_num'] = self.get_point_info(pid)['point_num']
        self.insert_into_db('fs_point_from',write_data)
        point_name = self.get_point_info(pid)['name']
        self.send_sysinfo(uid,point_name,'积分提示')
        return True

    def insert_into_db(self,table,data_dict):
        key_str = ''
        value_str = ''
        for key in data_dict:
            key_str += key + ','
            data_dict[key] = ("%s" % data_dict[key])
            value_str += '"' + data_dict[key] + '"' + ','
        key_str = ' (' + key_str[:-1] + ') '
        value_str = ' (' +  value_str[:-1] + ') '
        sql = "INSERT INTO %s %s VALUES %s" % (table,key_str,value_str)
        try: result = self.db.execute(sql)
        except Exception,e: self.treat_except(e)
        return result

    def get_game_only_level_event(self,gid):
        gid = str(gid)
        eid_list = []
        if not self.cacheRedis.exists('game_only_level:id:' + gid):
            eid_info_list = self.db.query("SELECT eid FROM fs_events WHERE gid=%s",gid)
            for eid_info in eid_info_list:
                eid_list.append(eid_info['eid'])
            self.cacheRedis.set('game_only_level:id:' + gid,eid_list)
        return self.cacheRedis.get('game_only_level:id:' + gid)



    def incr_game_attend_num(self,eid,incr_num):
        eid = str(eid)
        event_info = self.get_event_info(eid)
        gid = event_info['gid']
        try:
            self.db.execute("UPDATE fs_games_new SET gattend = gattend + %s WHERE gid = %s",incr_num,gid)
            if self.cacheRedis.exists('game:id:' + gid):
                self.cacheRedis.hincrby('game:id:' + gid,'gattend',incr_num)
            self.db.execute("UPDATE fs_events SET eattend = eattend + %s WHERE eid = %s",incr_num,eid)
            if self.cacheRedis.exists('event_info:id:' + eid):
                self.cacheRedis.hincrby('event_info:id:' + eid,'eattend',incr_num)
        except Exception,e: self.treat_except(e)
        return True

    def check_event_available(self,eid,new_attend_num):
        """check if the attend time has end  or the num is full   first check the time, and second check the max_num_attend"""
        event_info = self.get_event_info(eid)
        gacceptend = self.get_game_info(event_info['gid'],['gacceptend','gattend'])['gacceptend']
        if int(time.time()) >  gacceptend:  return 1 # attend end         
        return 2 if int(event_info['eattend']) + int(new_attend_num) > int(event_info['emaxattend']) and int(event_info['emaxattend']) else True

    def get_event_info(self,eid):
        eid = str(eid)
        if not self.cacheRedis.exists('event_info:id:' + eid):
            try:
                event_info_db = self.db.get("SELECT * FROM fs_events WHERE eid = %s",eid)
                self.cacheRedis.hmset('event_info:id:' + eid,event_info_db)
            except Exception,e: self.treat_except(e)
        try:  event_info = self.cacheRedis.hgetall('event_info:id:' + eid)
        except Exception,e: self.treat_except(e)  
        return event_info

    def get_check_status_name(self,checkstatus,is_group):
        checkstatus = str(checkstatus)
        status_name_dict = {'1':'审核中','2':'attend 成功','3':'attend fail'}
        status_name_dict['0'] = '支付' if is_group  else '未支付'
        return status_name_dict[checkstatus]
        
    def get_user_attend_list(self,uid,info_list):
        return self.find_some('fs_user_event',info_list,uid=uid,status=0)

    def justify_user_attend(self,eid,idcard):
        try:  count = self.find_db_sum('fs_user_event',eidcard=idcard,eid=eid)
        except Exception,e: self.treat_except(e)
        return True if count > 0 else False

    def check_point_have_get(self,uid,pid):
        return self.find_db_sum('fs_point_from',uid=uid,pid=pid)

    def get_full_event_name(self,eid):
        """get the event_class event_belong to and glue the classname and event name"""
        eid = str(eid)
        name_return = ''
        if not self.cacheRedis.exists('event_all_name:id:' + eid):
            try:
                event_info = self.db.get("SELECT upid,ename FROM fs_events WHERE eid = %s",eid)
                name_return += event_info['ename']
                eid_upid_info = self.db.get("SELECT level,upid,name FROM fs_events_class WHERE id = %s",event_info['upid'])
                if eid_upid_info is None: return name_return
                name_return = eid_upid_info['name'] + '-' + name_return
                if eid_upid_info['level'] == 1:
                    top_level_info = self.db.get("SELECT name FROM fs_events_class WHERE id=%s",eid_upid_info['upid'])
                    name_return = top_level_info['name'] + '-' + name_return
            except Exception,e: self.treat_except(e)
            return name_return   

    def addEventMem(self,public_info,mem_info):
        event_info_write = dict(public_info,**mem_info)
        sql = 'INSERT INTO fs_user_event '
        key_str = ''
        value_str = '' 
        for key in event_info_write:
            key_str += key + ','
            event_info_write[key] = ("%s" % event_info_write[key]) #change the str code type
            value_str += '"' + event_info_write[key] + '"' + ','
        key_str = '(' + key_str[0:-1] + ')'
        value_str = '(' + value_str[0:-1] + ')'
        sql += key_str + ' VALUES ' + value_str
        try:  self.db.execute(sql)
        except: return False
        return True

    #get group_list via uid 
    def get_group_list_via_uid(self,uid):
        uid = str(uid)
        list_return = []
        if not self.cacheRedis.exists('mygroup:uid:' + uid):
            group_id_list_db = self.db.query("SELECT group_id FROM fs_group_mem  WHERE uid = %s and is_leader=0",uid)
            for group_id in group_id_list_db:
                self.cacheRedis.lpush('mygroup:uid:' + uid,group_id['group_id']);
                list_return.append(group_id['group_id'])
        list_return = self.cacheRedis.lrange('mygroup:uid:' + uid,0,-1)
        return list_return

    def find_db_sum(self,table,**query_dict):
        """input dict and return the count of query """
        sql = "SELECT COUNT(*) AS sum FROM " + table + ' WHERE '
        for index in query_dict:
            if not isinstance(query_dict[index],dict): sql += " %s = '%s' and" % (index,query_dict[index]) 
            else:   sql += " %s %s '%s' and" % (index,query_dict[index]['rule'],query_dict[index]['value'])
        sql = sql[0:-3]
        # self.out(sql)
        try: sum = self.db.get(sql)['sum']
        except Exception,e: self.treat_except(e)
        return int(sum) if int(sum) else False

    def find_some(self,table,field_list,**query_dict):
        """find some data from the db is is_all is True then fetch all data """
        start_sql = 'SELECT '
        sql = ''
        query_sql = ''
        for field in field_list: start_sql += field + ',' 
        start_sql = start_sql[0:-1] + ' FROM %s WHERE ' % (table)
        try:
            if query_dict:
                for index in query_dict:
                    if not isinstance(query_dict[index],dict): query_sql += " %s = '%s' and" % (index,query_dict[index]) 
                    else:   query_sql += " %s %s '%s' and" % (index,query_dict[index]['rule'],query_dict[index]['value'])
            sql = (start_sql + query_sql)[0:-3]   
            info_list = self.db.query(sql)
        except Exception,e: self.treat_except(e)     
        return info_list

    def find_one(self,table,field_list,**query_dict):
        """find some data from the db is is_all is True then fetch all data """
        start_sql = 'SELECT '
        sql = ''
        query_sql = ''
        for field in field_list: start_sql += field + ',' 
        start_sql = start_sql[0:-1] + ' FROM %s WHERE ' % (table)
        try:
            if not query_dict: query_sql = '*'
            else:
                for index in query_dict:
                    if not isinstance(query_dict[index],dict): query_sql += " %s = '%s' and" % (index,query_dict[index]) 
                    else:   query_sql += " %s %s '%s' and" % (index,query_dict[index]['rule'],query_dict[index]['value'])
            sql = (start_sql + query_sql)[0:-3]   
            info = self.db.get(sql)
        except Exception,e: self.treat_except(e)     
        return info

    def get_early_night_timestamp(self):
        date_str_info = time.strftime("%Y-%m-%d",time.localtime(int(time.time())))
        date_array_some = time.strptime(date_str_info,"%Y-%m-%d")
        timestamp = int(time.mktime(date_array_some))
        return timestamp

    def judge_today_point_give(self,uid,pid,gid=0):
        """ the attribute of some point may only give once a day ,so we should judge if the user has been given"""
        early_night_timestamp = self.get_early_night_timestamp()
        return self.find_db_sum('fs_point_from',uid=uid,pid=pid,gid=gid,time={'rule':'>','value':early_night_timestamp})

    def get_user_who_attend_event(self,eid):
        """this method only fetch out head 100 users order by """
        eid = str(eid)
        if not self.cacheRedis.exists("user_attend_event:eid:" + eid):
            uidList = self.db.query("SELECT uid FROM fs_user_event WHERE eid=%s and status=0",eid)

    def check_have_attend_by_uid(self,uid,eid):
        """
         if the user(uid) have attend the event, then it will return true else return false
        """
        uid = str(uid)
        eid = str(eid)
        count_info = self.db.get("SELECT COUNT(*) AS num FROM fs_user_event WHERE uid=%s and eid=%s and status=0 and checkstatus = 2",uid,eid)
        return True if count_info['num'] else False

    def get_recent_run_man(self,eid):
        """
          get the recent 6 users who attend the event 
          each time the process fetch 10 rows rundata from table and check if the user has attend the specific events and if when after check 10 rows data ,we also can not 
          fetch out the 6 recent users, then we should fetch more 10 rows from the table and repeat the operation. 
          and we should also care about the case which there is no more than 6 users attend the event
          this place read list str  from redis and eval to list of python 
        """
        eid = str(eid)
        show_num = 6
        recent_man_list = [] # use list to ensure there is no repeat one 
        jump = 0
        if not self.cacheRedis.exists("recent_run_man:eid:" + eid):
            try:
                while len(recent_man_list) < show_num:
                    user_list = self.db.query("SELECT uid,step_count AS step FROM fs_rundata WHERE status=0 order by id desc limit %s,%s",jump,jump+5)
                    if not user_list: break
                    jump = jump + 5
                    for user_info in user_list:
                        if  user_info not in recent_man_list and self.check_have_attend_by_uid(user_info['uid'],eid):
                            recent_man_list.append(user_info)
                            if len(recent_man_list) == show_num: break
                self.cacheRedis.set("recent_run_man:eid:" + eid,recent_man_list,options.recent_run_man)   
            except Exception,e: self.treat_except(e)
        return eval(self.cacheRedis.get("recent_run_man:eid:" + eid))
 
    def alreay_in_group(self,uid,group_id):
        """  #justify if already in the group ok the input user is not the leader """
        uid = str(uid)
        user_group_list = self.get_group_list_via_uid(uid)
        return True if group_id in user_group_list else False

    def get_tag_info(self,tag_id):
        tag_id = str(tag_id)
        if not self.cacheRedis.exists('tag:id:' + tag_id):
            tag_info = self.db.get("SELECT * FROM fs_tag WHERE id = %s",tag_id)
            self.cacheRedis.set('tag:id:' + tag_id + ':name',tag_info['name'])
        return self.cacheRedis.get('tag:id:' + tag_id + ':name')

   #input a list and add the rank string into the list elment  
    def add_rank_string(self,input_list):
        for index,ele in enumerate(input_list):
            input_list[index]['rank_string'] = '第' + str(index + 1) + '名'

   #template output data 
    def return_param(self,result,flag,data,desc):
        return_dict = {'result':result,'flag':flag,'data':data,'desc':desc}
        try: self.finish(return_dict)
        except: return 

   #read group info from cache if not exist then read from mysql and save it to cache 
    def group_info_read(self,group_id):
        group_info = self.cacheRedis.hgetall('group:id:' + group_id)
        if not group_info:#if not in cache 
            group_info = self.db.get('SELECT * FROM fs_group WHERE id = %s',group_id)
            self.cacheRedis.hmset('group:id:' + group_id,group_info) #add info to cache s
        return group_info
   #get userid via tel 
    def get_uid_via_tel(self,tel):
        uid = self.cacheRedis.get('users:tel:' + tel)
        if not uid:# if not in cache read from mysql 
            uid = self.db.get('SELECT uid FROM fs_users WHERE tel = %s LIMIT 1',tel)#read from mysql
            if not uid:
                return False
            uid = uid['uid']
            self.cacheRedis.set('users:tel:' + tel,uid) #write into cache
        return uid

   #get age by idcard 
    def get_age_via_idcard(self,idcard):
        bir_year = int(idcard[6:10])
        now_year = int(time.strftime("%Y",time.localtime()))
        age =  now_year - bir_year
        return age if age > 0 else 0

   #get the group_user_list \ input the group_id  and it will return the list of uid in this group 
    def get_group_user_list(self,group_id):
       group_user_list_exists = self.cacheRedis.exists('group_user_list:group_id:' + str(group_id))
       if  not group_user_list_exists:#if not in cache 
           group_user_list = self.db.query('SELECT uid FROM fs_group_mem where group_id = %s',str(group_id))
           if not group_user_list:#if there is no body in the group 
               return []#this is nobody in the group
           for uid_info in group_user_list:
               self.cacheRedis.rpush('group_user_list:group_id:' + str(group_id),uid_info['uid'])
       self.cacheRedis.expire('group_user_list:group_id:' + str(group_id),options.group_user_list_expires)
       group_user_list = self.cacheRedis.lrange('group_user_list:group_id:' + str(group_id), 0,-1)
       return group_user_list  #return the list of the xxx

    #get the userinfo of input param  the search_param may like username user_password etc or a list or a tuple 
    def get_userinfo_via_search_param(self,search_param,uid):
        uid = str(uid)
        if not self.cacheRedis.exists('users:uid:' + uid):# if this user info is not exist then read from mysql and write to cache
            path = options.ipnet
            userinfo = self.db.get("SELECT username,password,tel,token,idcard,login_times,sex,nickname,last_login,CONCAT(%s,avatar) AS avatar,point FROM fs_users WHERE uid = %s",path,uid)
            self.cacheRedis.hmset('users:uid:' + uid,userinfo)
            self.cacheRedis.expire('users:uid:' + uid,options.user_info_expires)
        if isinstance(search_param,str):#if only search one 
            return self.cacheRedis.hget('users:uid:' + uid,search_param) #return string 
        else: #the type of search_param is list 
            user_info = self.cacheRedis.hmget('users:uid:' + uid,search_param) #return list  ['yinnananan', '111111']
            user_info_return = {}
            for index,param in enumerate(search_param):
                user_info_return[param] = user_info[index]
            user_info_return['uid'] = uid
            return user_info_return 

    def update_db(self,table,change_param,where,update_type='reset'):
        """the change_param is dict  reset the db info and the default oper is reset and also have add but the add may + or -  """
        try:
            change_sql = "UPDATE %s SET" % (table)
            for key in change_param:
                if update_type == 'reset':
                    change_sql += " %s='%s'," % (key,change_param[key])
                elif update_type == 'add':
                    change_sql += " %s=%s+%s," % (key,key,change_param[key])
            change_sql = change_sql[0:-1] + ' WHERE'
            for key in where:
                change_sql += " %s='%s' and " % (key,where[key])
            change_sql = change_sql[0:-4]
            self.db.execute(change_sql)
        except Exception,e: self.treat_except(e)
        return True

    #sort user by point   
    def sort_by_param(self,list_of_dict,param,reverse=True):
        return sorted(list_of_dict,key=operator.itemgetter(param),reverse=reverse)
        
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.db.get("SELECT * FROM authors WHERE id = %s", int(user_id))

    def createCookies(self):
        str = ''.join(sample('abcdefghijklmnopqrstuvwxyz1234567890^&*()$#@!',8))
        return str

    def get_token(self,uid):
        uid = str(uid)
        if self.cacheRedis.exists('users:uid:' + uid ): token = self.cacheRedis.hget('users:uid:' + uid,'token')
        else: token = self.find_one('fs_users',['token'],uid=uid)['token']
        return token

    #send system info 
    def send_sysinfo(self,uid,content,title):
        self.insert_into_db('fs_sysinfo',{'uid':uid,'content':content,'title':title,'time':int(time.time())})

    #get group info   return dict 
    def get_group_info(self,group_id):
        group_id = str(group_id)
        group_info = self.cacheRedis.hgetall('group:id:' + group_id)  
        if not group_info:#data not in cache so read from mysql and write into cache 
            group_info = self.find_one('fs_group',['*'],id=group_id)
            group_info['createtime'] = time.strftime("%Y-%m-%d",time.localtime(group_info['createtime']))
            group_info['tag_name'] = self.get_tag_info(group_info['tag_id'])
            group_info['avatar'] = options.ipnet + str(group_info['avatar'])
            self.cacheRedis.hmset('group:id:' + group_id,group_info) #write into cache
            self.cacheRedis.expire('group:id:' + group_id,options.group_info_expires)
        return group_info

    #get game info  by input param, if param if all,so fetch all param,else fetch the value in input param list 
    def get_game_info(self,game_id,param='all'):
        #save to cache 
        game_id = str(game_id)
        if not self.cacheRedis.exists('game:id:' + game_id):
            game_info = self.db.get("SELECT * FROM fs_games_new WHERE gid=%s",game_id)
            self.cacheRedis.hmset('game:id:' + game_id, game_info)
            self.cacheRedis.expire('game:id:' + game_id,options.game_info_expires)
        game_info_dict = {}
        if param == 'all':
            game_info_dict = self.cacheRedis.hgetall('game:id:' + game_id)
        else:  ####in this place we do not justify the time 
            game_info = self.cacheRedis.hmget('game:id:' + game_id,param)
            for index,value in enumerate(param):
                game_info_dict[value] = game_info[index]
        return game_info_dict

   #justify the game_status?? game start,game end game accept sign  game stop sign start game xxx 
    def make_game_info(self,game_info,uid,param='all'):
        """
          gstatusid  0 game start  1 sign start   2 sign not start   3 sign end    4 game end  
          in this function the attribute of time will be removed 
        """
        game_start = int(game_info['gstarttime'])
        game_end = int(game_info['gendtime'])
        sign_start = int(game_info['gacceptstart'])
        sign_end = int(game_info['gacceptend'])
        nowtime = int(time.time())
        # game_start = 1459085648
        if nowtime > game_end:
             dict_return = {'gstatusid':4,'gstatus':"赛事结束"}
        elif nowtime > game_start:
             dict_return = {'gstatusid':0,'gstatus':'赛事开始'}
        elif nowtime > sign_end:
             dict_return = {'gstatusid':3,'gstatus':'报名结束'}
        elif nowtime > sign_start:
             dict_return = {'gstatusid':1,'gstatus':'接受报名'}
        else:
             dict_return = {'gstatusid':2,'gstatus':'报名未开始'}
        if param != 'all':
            dict_return['gid'] = game_info['gid']
            dict_return['startmap'] = game_info['startmap']
            dict_return['sport_type'] = game_info['sport_type']
            return dict_return

        game_info['gacceptstartdate'] = time.strftime("%Y-%m-%d",time.localtime(sign_start))
        game_info['gacceptenddate'] = time.strftime("%Y-%m-%d",time.localtime(sign_end))
        game_info.pop('gstarttime')
        game_info.pop('gendtime')
        game_info.pop('gacceptstart')
        game_info.pop('gacceptend')
        game_info.pop('gouttime')
        game_info.pop('status')
        game_info.pop('gcheckstatus')
        host = options.ipnet
        game_info['gfrontpage'] = host + game_info['gfrontpage']
        # /py/game?action=game_live&id=' + str(live['id'])
        game_info['agreement'] = host + '/py/game?action=get_agreement&id=' + str(game_info['gid'])
        game_info['gintro'] = host + '/py/game?action=get_intro&id=' + str(game_info['gid']) + \
        '&uid=' + str(uid) + '&gtype=' + str(game_info['gtype_id'])
        game_info['gintro_wecha'] = host + '/ky/game?action=get_intro&id=' + str(game_info['gid']) + \
        '&uid=' + str(uid) + '&gtype=' + str(game_info['gtype_id'])
        game_info.update(dict_return)
        return game_info

  #def debug 
    def out(self,ouput):
        self.write(str(ouput))

   #get game type  zuqiu  paobu 
    def get_game_type(self,type_id='all'): 
       if not self.cacheRedis.exists('gametype'):
           type_info = self.db.query("SELECT * FROM fs_gametype")
           self.cacheRedis.set('gametype',type_info)
       type_info = self.cacheRedis.get('gametype')
       for type_info_ele in eval(type_info):
           if not self.cacheRedis.exists('gametype:id:' + str(type_info_ele['id'])):
               self.cacheRedis.set('gametype:id:' + str(type_info_ele['id']),type_info_ele['name'])
       if type_id == 'all':
           return eval(type_info)
       else:
           return self.cacheRedis.get('gametype:id:' + str(type_id))

    #def get_game_level  if the level_id is 
    def get_game_level(self,level_id='all'):
        if not self.cacheRedis.exists('gamelevel'):
            level_info = self.db.query("SELECT * FROM fs_leveltype")
            self.cacheRedis.set('gamelevel',level_info)
        level_info = self.cacheRedis.get('gamelevel')
        for level_info_ele in eval(level_info):
            if not self.cacheRedis.exists('gamelevel:id:' + str(level_info_ele['id'])):
                self.cacheRedis.set('gamelevel:id:' + str(level_info_ele['id']),level_info_ele['name'])
        if level_id == 'all':
            return eval(level_info)
        else:
            return self.cacheRedis.get('gamelevel:id:' + str(level_id))


class TestHandler(BaseHandler):
    def get(self):
        self.out(options.lpf)
        # my = Test()
        # my.test()



class AttendHandler(BaseHandler):
    run_game_not_need_check_type = (2,3) #save the game type  not need pay and dont need check
    def get_first_level_filter(self,gid,is_group):
        """
         in this function,we only remove the "class" which has no events! 
        """
        first_level_list = self.get_first_level(gid,is_group)
        if not first_level_list: return []  # if there if nothing in the first level,then return []
        for index_first,info_first in enumerate(first_level_list):
            if int(info_first['is_event']): continue  #if there has event under the current class,then reserve the first_level class
            second_level_list = self.get_second_level(info_first['id'],is_group)
            if not second_level_list:
                del first_level_list[index_first]
                continue
            for index_second,info_second in enumerate(second_level_list):
                if int(info_second['is_event']): break #if there has event under the current second class,then reserve the first_level_class
                else:
                    third_level_list = self.get_third_level(info_second['id'],is_group)
                    if third_level_list: break # if there is no event under the second class,then remove the first level class 
                del first_level_list[index_first]
        return first_level_list

    def get_second_level_filter(self,id,is_group):
        """
           in this function,we only remove the "class" which has no events! and we can make sure that second_level_list is not []
        """
        second_level_list = self.get_second_level(id,is_group)
        for index_second,info_second in enumerate(second_level_list):
            if int(info_second['is_event']): continue
            third_level_list = self.get_third_level(info_second['id'],is_group)
            if not third_level_list: del second_level_list[index_second]
        return second_level_list

    def get_first_level(self,gid,is_group):
        gid = str(gid)
        if int(is_group):
            find_sql = ' and  event_type <> 2'
            redis_key = 'first_level_group:gid:' + gid
        else: 
            find_sql = ' and event_type <> 3'
            redis_key = 'first_level_person:gid:' + gid
        if not self.cacheRedis.exists(redis_key):
            try:
                level1_event_sql = 'SELECT eid AS id,ename AS name,epayfee,group_max,group_min FROM fs_events WHERE gid=%s and status=0 and upid=0 '  % (gid) + find_sql
                level1_event_list = self.db.query(level1_event_sql)
                for index,event in enumerate(level1_event_list):
                    event['is_event'] = 1
                    level1_event_list[index] = event
                level1_class_list =  self.db.query('SELECT id,name FROM fs_events_class WHERE level=0 and status= 0 and gid = %s',gid)
                for index,classInfo in enumerate(level1_class_list):
                    classInfo['is_event'] = 0
                    level1_class_list[index] = classInfo
                first_level_return = level1_event_list + level1_class_list
                self.cacheRedis.set(redis_key,first_level_return)
            except Exception,e: self.treat_except(e)
        try: first_level_return = self.cacheRedis.get(redis_key)
        except Exception,e: self.treat_except(e)
        return eval(first_level_return)

    def get_second_level(self,id,is_group):
        id = str(id)
        if int(is_group):
            find_sql = ' and event_type <> 2'
            redis_key = 'second_level_group:id:' + id
        else:
            find_sql = ' and event_type <> 3'
            redis_key = 'second_level_person:id:' + id 
        if not self.cacheRedis.exists(redis_key):
            try:
                level2_event_sql = 'SELECT eid AS id,ename AS name,epayfee,group_max,group_min FROM fs_events WHERE  status=0 and upid= %s' % (id) + find_sql
                level2_event_list = self.db.query(level2_event_sql)
                for index,event in enumerate(level2_event_list):
                    event['is_event'] = 1
                    level2_event_list[index] = event
                level2_class_list =  self.db.query('SELECT id,name FROM fs_events_class WHERE status=0 and upid = %s',id)
                for index,classInfo in enumerate(level2_class_list):
                    classInfo['is_event'] = 0
                    level2_class_list[index] = classInfo
                second_level_return = level2_event_list + level2_class_list 
                print second_level_return
                self.cacheRedis.set(redis_key,second_level_return)
            except Exception,e: self.treat_except(e)
        try:  second_level_return = self.cacheRedis.get(redis_key)
        except Exception,e:  self.treat_except(e)
        return eval(second_level_return)

    def get_third_level(self,id,is_group):
        id = str(id)
        if int(is_group):
            find_sql = ' and event_type <> 2'
            redis_key = 'third_level_group:id:' + id 
        else:
            find_sql = ' and event_type <> 3' 
            redis_key = 'third_level_person:id:' + id
        if not self.cacheRedis.exists(redis_key):
            try:
                level3_event_sql = 'SELECT eid AS id,ename AS name,epayfee,group_max,group_min FROM fs_events WHERE  status=0 and upid= %s' % (id) + find_sql
                level3_event_list = self.db.query(level3_event_sql)
                for index,eventInfo in enumerate(level3_event_list):
                    eventInfo['is_event'] = 1
                    level3_event_list[index] = eventInfo
                self.cacheRedis.set(redis_key,level3_event_list)
            except Exception,e: self.treat_except(e)
        try: level3_event_list = self.cacheRedis.get(redis_key)
        except Exception,e: self.treat_except(e)
        return eval(level3_event_list)
 
    def get(self):
        action = self.get_argument('action')
        if action == 'get_first_level':
            """ in fact in this place,we also should justify if there is events under the class,and if not have ,then remove the class """
            is_group = self.get_argument('is_group') #justify if it need the group event
            gid = self.get_argument('gid')
            first_level_return = self.get_first_level_filter(gid,is_group)
            self.return_param(1,0,first_level_return,'成功')
        elif action == 'get_second_level':
            is_group = self.get_argument('is_group') #justify if it need the group event
            id = self.get_argument('id')
            second_level_return = self.get_second_level_filter(id,is_group)
            self.return_param(1,0,second_level_return,'成功')
        elif action == 'get_third_level':
            id = self.get_argument('id')
            is_group = self.get_argument('is_group') #justify if it need the group event
            level3_event_list = self.get_third_level(id,is_group)
            self.return_param(1,0,level3_event_list,'成功')
        elif action == 'group_attend':
            a_d = self.get_multi_argument(['id','eid','gid','leader_name','leader_tel','leader_email','org_name','mem_str',{'version':False,'token':False,'uid':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # for that there is no  uid 
            mem_list = a_d['mem_str'].split(',')
            available_sign = self.check_event_available(a_d['eid'],len(mem_list))
            if available_sign is 1: return self.return_param(0,201,{},'报名已经结束')
            if available_sign is 2: return self.return_param(0,200,{},'该项目报名名额已满')
            out_trade_no = self.create_out_trade_num()
            write_data = self.treat_ar_dict(a_d,['id','version','token','mem_str'],group_id=a_d['id'],out_trade_no=out_trade_no,attendtime = int(time.time()))
            epayfee = self.get_event_info(a_d['eid'])['epayfee']
            game_info = self.get_game_info(a_d['gid'])
            gtype_id = int(game_info['gtype_id'])
            if not float(epayfee):  write_data['checkstatus'] = 1
            if gtype_id in self.run_game_not_need_check_type: write_data['checkstatus'] = 2
            for uid in mem_list:
                mem_info = self.get_userinfo_via_search_param(['username','tel','avatar','idcard','sex'],uid)
                picPath = mem_info['avatar'][mem_info['avatar'].index('/Uploads'):]
                age = self.get_age_via_idcard(mem_info['idcard'])
                mem_info_write = {'eusername':mem_info['username'],'etel':mem_info['tel'],'picPath':picPath,'eidcard':mem_info['idcard'],'esex':mem_info['sex'],'eage':age,'uid':uid}
                info = dict(write_data,**mem_info_write)
                result = self.insert_into_db('fs_user_event',info)
            self.incr_game_attend_num(a_d['eid'],len(mem_list))
            self.return_param(1,0,{'id':result},'成功')

            # self.checkTheInfo(mem_list)
        elif action == 'checkUserInfo':
            uid = self.get_argument('uid')
            eid = self.get_argument('eid')
            userInfo = self.get_userinfo_via_search_param(['sex','idcard','username','tel'],uid)
            warn_str = ''
            e2cdict = {'sex':'性别','idcard':'身份证号','username':'姓名','tel':'手机号码'}
            for info in userInfo:
                if userInfo[info] == '':
                    warn_str = '用户 ' + e2cdict[info] + ' 没有完善，请提示该用户完善信息' 
                    break;
            if warn_str: self.return_param(0,200,{},warn_str)
            have_attend = self.justify_user_attend(eid,userInfo['idcard'])
            if have_attend: self.return_param(0,201,{},'用户已经报名了该项目')
            self.return_param(1,0,{},'允许')

        elif action == 'get_all_attend':
            uid = self.get_argument('uid') 
            user_attend_list = self.get_user_attend_list(uid,['gid','eid','ueid','eusername','group_id','checkstatus','eage','esex','etel','eidcard'])
            for index,attend_info in enumerate(user_attend_list):
                user_attend_list[index]['epayfee'] = self.get_event_info(attend_info['eid'])['epayfee']
                user_attend_list[index]['ename'] = self.get_full_event_name(attend_info['eid'])
                game_info  = self.get_game_info(attend_info['gid'],['gstarttime','gfrontpage','gname'])
                user_attend_list[index]['start_time'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(int(game_info['gstarttime'])))
                user_attend_list[index]['gfrontpage'] =  options.ipnet + game_info['gfrontpage']
                user_attend_list[index]['gname'] = game_info['gname']
                user_attend_list[index]['gposition'] = '北京'
                user_attend_list[index]['click_brief'] = options.ipnet + '/py/attend?action=attend_brief&id=' + str(attend_info['ueid'])
                user_attend_list[index]['agreement'] = options.ipnet + '/py/system?action=get_agreement&gid=' + str(attend_info['gid'])
                # user_attend_list[index]
                if attend_info['group_id']:
                    user_attend_list[index]['is_group'] = 1
                    user_attend_list[index]['attend_show'] = self.get_group_info(attend_info['group_id'])['group_name']
                    user_attend_list[index]['status_name'] = self.get_check_status_name(attend_info['checkstatus'],1)
                else:
                    user_attend_list[index]['attend_show'] = attend_info['eusername']
                    user_attend_list[index]['status_name'] = self.get_check_status_name(attend_info['checkstatus'],0)
            self.return_param(1,0,user_attend_list,'成功')

        elif action == 'attend_brief':
            self.out('this is the brief  in develop')

        elif action == 'person_attend':
            a_d = self.get_multi_argument(['uid','eid','gid','eidcard','eusername','esex','etel','org_name',{'version':False,'token':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
            age = self.get_age_via_idcard(a_d['eidcard'])
            if self.justify_user_attend(a_d['eid'],a_d['eidcard']): self.return_param(0,200,{},'你已经报名了该项目')
            available_sign = self.check_event_available(a_d['eid'],1)
            if available_sign is 1:  self.return_param(0,201,{},'报名结束')
            if available_sign is 2:  self.return_param(0,202,{},'该项目报名名额已满')
            data_write = self.treat_ar_dict(a_d,['token','version'],eage=age,attendtime=int(time.time()))
            user_avatar = self.get_userinfo_via_search_param(['avatar'],a_d['uid'])['avatar']
            data_write['picPath'] =   user_avatar[user_avatar.index('/Uploads'):] 
            epayfee = self.get_event_info(a_d['eid'])['epayfee']
            game_info = self.get_game_info(a_d['gid'])
            gtype_id = int(game_info['gtype_id'])
            #if the game type if person not need payfee then we set the checkstatus 2 
            if not float(epayfee): data_write['checkstatus'] = 1 # the event is free
            else: data_write['out_trade_no'] = self.create_out_trade_num()
            if gtype_id in self.run_game_not_need_check_type: data_write['checkstatus'] = 2 #the type of the game dont need pay and dont need check
            pri_id = self.insert_into_db('fs_user_event',data_write)
            self.incr_game_attend_num(a_d['eid'],1)
            self.return_param(1,0,{'id':pri_id},'成功')

class MapHandler(BaseHandler):

    def get(self):
        a_d_head = self.get_multi_argument(['uid','version','token','action'])
        if a_d_head['version'] == options.token_request_more_version: self.check_token_available(a_d_head['uid'],a_d_head['token'])
        if a_d_head['action'] == 'get_run_belong':
            belong_sn = a_d_head['uid'] + str(self.get_current_timestamp())
            self.return_param(1,0,{'belong_sn':belong_sn},'success')
        # elif a_d_head['action'] == ''


class GameHandler(BaseHandler):
    def get_all_game_id(self):
        if not self.cacheRedis.exists('game_id_link'):
            game_id_link = self.db.query("SELECT gid FROM fs_games_new WHERE status = 0")
            for game_info in game_id_link:
                self.cacheRedis.lpush('game_id_link',game_info['gid'])
        return self.cacheRedis.lrange('game_id_link',0,-1)
        # def sort_by_param(self,list_of_dict,param,reverse):
        # return sorted(list_of_dict,key=operator.itemgetter(param),reverse=reverse)

    def get(self):
        action = str(self.get_argument('action'))
        if action == 'front_page':
            uid = self.get_argument('uid',0)
            if int(uid):
                if  self.check_point_have_get(uid,4) == 0:#first time login then give 50000 point
                    self.give_point(uid,50000)
                    self.write_user_point_from(uid,4,0)
                    point_info = self.get_point_info(4)
                    self.send_sysinfo(uid,point_info['name'],'系统消息')
            game_id_link = self.get_all_game_id()
            game_info_list = []
            for gid in game_id_link:
               game_info = self.get_game_info(gid,'all')
               game_info_list.append(self.make_game_info(game_info,uid))
            game_info_return =  self.sort_by_param(game_info_list,'gstatusid',False)
            self.return_param(1,0,game_info_return,'成功')
       
        elif action == 'get_game_info':
            gid = self.get_argument('gid')
            uid = self.get_argument('uid',0) #this place is not need but no time to youhua
            game_info = self.get_game_info(gid,'all')
            game_info = self.make_game_info(game_info,uid,'not all') #just fetch out some param is ok 
            host = options.ipnet
            self.return_param(1,0,game_info,'成功')

        elif action == 'rank_test':
            uidList = self.get_user_attend_event(8)

        elif action == 'get_game_lives':
            gid = str(self.get_argument('gid'))
            if not self.cacheRedis.exists('gamelives:gid:' + gid):
                lives_info_db = self.db.query("SELECT * FROM fs_lives WHERE gid = %s",gid)
                lives_info = []
                for live in lives_info_db:
                    live['time'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(live['time']))
                    live['pic'] = options.ipnet + live['pic']
                    live['content'] = options.ipnet + '/py/game?action=get_live&id=' + str(live['id'])
                    lives_info.append(live)
                self.cacheRedis.set('gamelives:gid:' + gid,lives_info)
                self.cacheRedis.expire('gamelives:gid:' + gid,options.game_lives_expires)
            lives_info = self.cacheRedis.get('gamelives:gid:' + str(gid))
            self.return_param(1,0,eval(lives_info),'成功')

        elif action == 'get_live':
            id = str(self.get_argument('id'))
            if not self.cacheRedis.exists('live_info:id:' + id):
                live_info_db = self.db.get("SELECT content FROM fs_lives WHERE id=%s",id)
                self.cacheRedis.set('live_info:id:' + id,live_info_db['content'])
                self.cacheRedis.expire('live_info:id' + id,options.game_lives_expires)
            live_content = self.cacheRedis.get('live_info:id:' + id)
            self.write(live_content)

        elif action == 'game_score':
            id = str(self.get_argument('id'))
            if not self.cacheRedis.exists('score_info:id:' + id):
                score_info_db = self.db.get("SELECT content FROM fs_scores  WHERE id=%s",id)
                self.cacheRedis.set('score_info:id:' + id,score_info_db['content'])
            score_content = self.cacheRedis.get('score_info:id:' + id)
            self.write(str(score_content))

        elif action == 'get_game_score':
            gid = self.get_argument('gid')
            if not self.cacheRedis.exists('gamescores:gid:' + str(gid)):
                scores_info_db = self.find_some('fs_scores',['*'],gid=gid)
                for  index,score in enumerate(scores_info_db):
                    scores_info_db[index]['time'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(score['time']))
                    scores_info_db[index]['pic'] = options.ipnet + score['pic']
                    scores_info_db[index]['content'] = options.ipnet + '/py/game?action=game_score&id=' + str(score['id'])
                self.cacheRedis.set('gamescores:gid:' + str(gid),scores_info_db)
            scores_info = self.cacheRedis.get('gamescores:gid:' + str(gid))
            self.return_param(1,0,eval(scores_info),'成功')

        elif action == 'get_agreement':
            gid = str(self.get_argument('id'))
            if not self.cacheRedis.exists('game_agreement:id:' + gid):
                agreement_info_db = self.db.get('SELECT agreement FROM fs_games_new WHERE gid = %s',gid)
                self.cacheRedis.set('game_agreement:id:' + gid,agreement_info_db['agreement'])
                self.cacheRedis.expire('game_agreement:id:' + gid,options.game_agreement_expires)
            agreement = self.cacheRedis.get('game_agreement:id:' + gid)
            self.write(str(agreement))

        elif action == 'get_intro':
            gid =  self.get_argument('id')
            gtype =  self.get_argument('gtype')
            uid = self.get_argument('uid')
            if gtype == '2': #jianbuzou online personal sport 
                rank_url = options.ipnet + '/py/rank?action=get_person_jbz_run_rank&gid=' + gid + '&uid=' + uid + '&rank_param=day'
                brief_intro_url = options.ipnet + '/py/gamemore?action=get_game_brief&gid=' + gid
                recent_run_man = []
                game_info = self.get_game_info(gid)
                eid = eval(self.get_game_only_level_event(gid))[0]
                if int(game_info['gacceptend']) >  int(time.time()):#when the game is start,but there not consider the end of the game 
                    recent_run_man = self.get_recent_run_man(eid) #in fact the runing game only have one event
                    for index,user_run_info in enumerate(recent_run_man):
                        user_info = self.get_userinfo_via_search_param(['avatar','nickname'],user_run_info['uid'])
                        recent_run_man[index]['avatar'] = user_info['avatar']
                        recent_run_man[index]['nickname'] = user_info['nickname'] if user_info['nickname'] else '小跑男'
                else: recent_run_man = False #this is the case that the game not start 
                self.render('front' + gid + '.html',recent_run_man=recent_run_man,rank_url=rank_url,brief_intro_url=brief_intro_url)

            elif gtype == '5': #quanyuehui leixing 
                self.render('front' + gid + '.html')
            elif gtype == '4': #mashangpao 
                rank_url = options.ipnet + '/py/rank?action=get_msp_run_rank&gid=' + gid + '&uid=' + uid
                brief_intro_url = options.ipnet + '/py/gamemore?action=get_game_brief&gid=' + gid 
                self.render('front'+gid+'.html',rank_url=rank_url,brief_intro_url=brief_intro_url)
            elif gtype == '3':#jibuzou  jianbubang fangshan  online group/personal sport
                game_info = self.get_game_info(gid)
                eid = eval(self.get_game_only_level_event(gid))[0]
                if int(uid):
                    if not self.judge_today_point_give(uid,1,5): #if the user has not given this type of point h
                        point_info = self.get_point_info(1) # this game user point id is 1
                        self.write_user_point_from(uid,1,5) #write the from of the point 
                        self.give_point(uid,point_info['point_num'])#give user the point  there palce
                if int(game_info['gacceptend']) >  int(time.time()):#when the game is start,but there not consider the end of the game 
                    recent_run_man = self.get_recent_run_man(eid) #in fact the runing game only have one event
                    for index,user_run_info in enumerate(recent_run_man):
                        user_info = self.get_userinfo_via_search_param(['avatar','nickname'],user_run_info['uid'])
                        recent_run_man[index]['avatar'] = user_info['avatar']
                        recent_run_man[index]['nickname'] = user_info['nickname'] if user_info['nickname'] else '小跑男'
                else: recent_run_man = False #this is the case that the game not start 
                rank_url = options.ipnet + '/py/rank?action=get_jbz_person_group_rank&gid=' + gid + '&uid=' + uid + '&rank_param=day&attend_type=个人'
                brief_intro_url = options.ipnet + '/py/gamemore?action=get_game_brief&gid=' + gid
                self.render('front'+gid+'.html',rank_url=rank_url,brief_intro_url=brief_intro_url,recent_run_man=recent_run_man)

        elif action == 'get_all_lives':
            gid = self.get_argument('gid',0)
            if not gid:
                lives_info_db = self.find_some('fs_lives',['id','title','pic','time'])
            else: lives_info_db = self.find_some('fs_lives',['id','title','pic','time'],gid=gid)
            for index,live_info in enumerate(lives_info_db):
                lives_info_db[index]['time'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(live_info['time']))
                lives_info_db[index]['content'] = options.ipnet + '/py/game?action=get_live&id=' + str(live_info['id'])
                lives_info_db[index]['pic'] = options.ipnet + live_info['pic']
            self.return_param(1,0,lives_info_db,'成功')




class RankHandler(BaseHandler):
    type_table = {'day':'fs_person_rundata_day','week':'fs_person_rundata_week','month':'fs_person_rundata_month','quarter':'fs_person_rundata_quarter',\
                   'year':'fs_person_rundata_year'}
    type_group_table = {'day':'fs_group_rundata_day','week':'fs_group_rundata_week','month':'fs_group_rundata_month','quarter':'fs_group_rundata_quarter',\
                   'year':'fs_group_rundata_year'}
    time_local = time.localtime(int(time.time()))
    current_quarter = int(time.strftime("%m",time_local))/3 + 1
    search_param = {'day':time.strftime("%y%m%d",time_local), \
                    'week':time.strftime("%y%U",time_local), \
                    'month':time.strftime("%y%m",time_local),\
                    'quarter':time.strftime("%y",time_local) + str(current_quarter),\
                    'year':time.strftime("%y",time_local)}
    rank_param_e2c = {'day':'日','week':'周','month':'月','quarter':'季','year':'年'}

    def my_rank(self,uid,eid,type): #get the user person rank,make sure the user has attend the game before use this method 
        sql = "SELECT step FROM %s WHERE uid = %s and eid=%s and date='%s'" % (self.type_table[type],uid,eid,self.search_param[type])
        step_info = self.db.get(sql)
        if step_info is None:
            event_info = self.get_event_info(eid)
            return event_info['eattend'] 
        sql2 = "SELECT COUNT(*) AS num FROM %s WHERE eid=%s and step >= %s and date='%s'" % (self.type_table[type],eid,step_info['step'],self.search_param[type])
        my_rank = self.db.get(sql2)
        return my_rank['num']

    def my_group_rank(self,group_id,eid,type):#get the group rank of the man ,make sure the user has attend the game before use this method
        sql = "SELECT step FROM %s WHERE group_id = %s and eid=%s and date='%s'" % (self.type_group_table[type],group_id,eid,self.search_param[type])
        group_step_info = self.db.get(sql)
        if group_step_info is None:
            event_info = self.get_event_info(eid)
            return event_info['eattend']
        sql2 = "SELECT COUNT(*) AS num FROM %s WHERE eid=%s and step >= %s and date='%s'" % (self.type_group_table[type],eid,group_step_info['step'],self.search_param[type])
        my_group_rank = self.db.get(sql2)
        return my_group_rank['num']

    def get_my_run(self,uid,eid,type):
        """
          use in personal event and get my own rank of all the man,make sure user has attend the event before use this method 
        """
        sql = "SELECT * FROM %s WHERE uid=%s and eid=%s and date=%s" % (self.type_table[type],uid,eid,self.search_param[type])
        run_data = self.db.get(sql)
        avatar = self.get_userinfo_via_search_param(['avatar'],uid)['avatar']
        if run_data is None:#the user not run 
            return {'step':0,'distance':0,'avatar':avatar}
        else:
            run_data['avatar'] = avatar
            run_data['distance'] = round(run_data['distance']/1000.0,1)
        return run_data

    def get_my_group_run(self,group_id,eid,type):
        """
        use in group event and get my group rank of all the groups,make sure user has attend the event before use this method 
        """
        sql = "SELECT * FROM %s WHERE group_id=%s and eid=%s" % (self.type_group_table[type],group_id,eid)
        run_data = self.db.get(sql)
        avatar = self.get_group_info(group_id)['avatar']
        if run_data is None: return {'step':0,'distance':0,'avatar':avatar}
        run_data['avatar'] = avatar
        return run_data

    def second2str(self,sum_second):
        second = str(sum_second % 60)
        minute = str(sum_second / 60 % 60)
        hour = str(sum_second / 3600)
        if len(second) == 1: second  =  '0' + second 
        if len(minute) == 1:  minute = '0' + minute
        if len(hour) == 1:  hour = '0' + hour
        return hour + ':' + minute +  ':' + second 

    def get_person_popular_list(self,eid,type):#get 100
        """ return the dict list of the user list  order by the step count of the event  """
        eid = str(eid)
        if not self.cacheRedis.exists("person_popular_" + type + ":eid:" + eid):
            sql = "SELECT uid,step,duration FROM %s WHERE eid=%s and date='%s' order by step desc limit 100" % (self.type_table[type],eid,self.search_param[type])
            person_popular_list = self.db.query(sql)
            if not person_popular_list: return []
            self.cacheRedis.set("person_popular_" + type + ":eid:" + eid,person_popular_list,options.rank_data_expires)
        person_popular_list = eval(self.cacheRedis.get('person_popular_' + type + ':eid:' + eid))
        for index,user_popular_info in enumerate(person_popular_list):
            user_info = self.get_userinfo_via_search_param(['avatar','nickname'],user_popular_info['uid'])
            person_popular_list[index]['avatar'] = user_info['avatar']
            person_popular_list[index]['nickname'] = user_info['nickname']
            person_popular_list[index]['duration'] = self.second2str(user_popular_info['duration'])
        return person_popular_list #if there is no one run so it will return None

    def get_group_popular_list(self,eid,type): # return the list of the group 
        eid = str(eid)
        if not self.cacheRedis.exists("group_popular_" + type + ":eid" + eid):
            sql = "SELECT group_id,step,duration FROM %s WHERE eid=%s and date='%s' order by step desc limit 100" % (self.type_group_table[type],eid,self.search_param[type])
            group_popular_list = self.db.query(sql)
            if not group_popular_list: return []
            self.cacheRedis.set("group_popular_" + type + ":eid:" + eid,group_popular_list,options.rank_data_expires)
            group_popular_list = eval(self.cacheRedis.get('group_popular_' + type + ':eid:' + eid))
            for index,group_popular_info in enumerate(group_popular_list):
                group_info = self.get_group_info(group_popular_info['group_id'])
                group_popular_list[index]['avatar'] = group_info['avatar']
                group_popular_list[index]['nickname'] = group_info['group_name']
        return group_popular_list #if there is no one run so it will return None

    def get(self):
        action = self.get_argument('action')
        rank_param = self.get_argument('rank_param','day')
        uid = self.get_argument('uid')
        gid = self.get_argument('gid')
        eid = eval(self.get_game_only_level_event(gid))[0]
        if action == 'get_person_jbz_run_rank':#runing man online jianbuzou sport
            have_attend = self.check_have_attend_by_uid(uid,eid)
            person_popular_list = self.get_person_popular_list(eid,rank_param)
            if have_attend:
                my_rank = self.my_rank(uid,eid,rank_param)
                my_run = self.get_my_run(uid,eid,rank_param)
                self.render('person_run_rank' + gid + '.html',have_attend=have_attend,person_popular_list=person_popular_list,\
                           my_run=my_run,my_rank=my_rank,rank_param=rank_param,rank_param_e2c = self.rank_param_e2c[rank_param])
            else:
                self.render('person_run_rank' + gid + '.html',have_attend=have_attend,person_popular_list=person_popular_list, \
                             rank_param=rank_param,rank_param_e2c = self.rank_param_e2c[rank_param])
        elif action == 'get_msp_run_rank':#mashangpao 
            self.render('msp_run_rank' + gid + '.html')
        elif action == 'get_jbz_person_group_rank':#jianbuzou group/personal run rank
            """one man can only attend one event either group or person, and the man can not change it except for new reposite"""
            attend_type_get = self.get_argument('attend_type','个人') #param from url
            attend_type = -1 if uid == '0' else self.judge_attend_type(uid,eid)
            if attend_type_get == '个人':
                have_attend = True if attend_type == 0 else False
                my_rank =  self.my_rank(uid,eid,rank_param) if attend_type == 0 else ''
                my_run = self.get_my_run(uid,eid,rank_param) if attend_type == 0 else ''
                person_popular_list = self.get_person_popular_list(eid,rank_param)
                msg = '您还没有参加该项目，或者您参加了该赛事的团队项目'
                self.render('jbz_person_group_rank'+ gid + '.html',have_attend=have_attend,popular_list=person_popular_list,\
                                my_run=my_run,my_rank=my_rank,rank_param=rank_param,attend_type_get=attend_type_get,msg=msg,\
                                rank_param_e2c = '我本' + self.rank_param_e2c[rank_param]
                                )
            else: #the attend_type_get is group
                have_attend = True if attend_type > 0 else False
                my_group_rank = self.my_group_rank(attend_type,eid,rank_param) if attend_type > 0 else ''
                my_group_run  = self.get_my_group_run(attend_type,eid,rank_param) if attend_type > 0 else ''
                group_popular_list = self.get_group_popular_list(eid,rank_param)
                msg = '您还没有参加该项目，或者您参加了该赛事的个人项目'
                self.render('jbz_person_group_rank'+ gid + '.html',have_attend=have_attend,popular_list=group_popular_list,\
                                my_run=my_group_run,my_rank=my_group_rank,rank_param=rank_param,attend_type_get=attend_type_get,msg=msg,\
                                rank_param_e2c = '我的团队本' + self.rank_param_e2c[rank_param])

class PointbonusHandler(RankHandler):
    rank_range_full = [0,10,100,1000,3000,5000,10000]
    point_id_full = {'week':['5','6','7','8','9','10'],'month':['11','12','13','14','15','16'],'quarter':['17','18','19','20','21','22']}
    eid_of_full = 186 #186
    gid_of_full = 5

    def give_rank_uid_list_point(self,eid,type,point_id_list,gid,rank_range):
        sql = "SELECT uid FROM %s WHERE eid=%s and date=%s and status=0 order by step desc limit 10000" % (self.type_table[type],eid,self.search_param[type])
        uidList = self.db.query(sql)
        rank_range_copy = copy.deepcopy(rank_range)
        for index,uid_info in enumerate(uidList): 
            index = index + 1
            rank_range_copy.append(index)
            point_index = sorted(rank_range_copy).index(index)
            rank_range_copy.pop()
            self.give_point_and_write_point_from_send_sysinfo(uid_info['uid'],point_id_list[type][point_index-1],gid,point_num=False)

    def get(self):
        action = self.get_argument('action')
        if action == 'give_full_point_week_month_quater':
            a_d = self.get_multi_argument(['param']) # the param may like week month and quarter
            self.give_rank_uid_list_point(self.eid_of_full,a_d['param'],self.point_id_full,self.gid_of_full,self.rank_range_full)

class SnHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'justify_sn_valid':
            id = self.get_argument('id') #attend id   ueid
            uid = self.get_argument('uid') #user id 
            sn = self.get_argument('sn')
            attend_info = self.get_attend_info(id)
            gid = attend_info['gid']
            eid = attend_info['eid']
            is_group = 1 if int(attend_info['group_id']) > 0 else 0
            sn_valid = self.check_sn_valid(sn,eid)
            if sn_valid is 1: self.return_param(0,200,{},'邀请码已经被使用或者不正确')
            if sn_valid is 2: self.return_param(0,201,{},'邀请码已经过期')
            sn_id = sn_valid['id']  # the sn primary key
            if int(is_group):
                if self.sn_pay_notify_group(id,uid,sn_id) is False: self.return_param(0,202,{},'支付失败')
            else:
                if self.sn_pay_notify_person(id,uid,sn_id) is False: self.return_param(0,202,{},'支付失败')
            self.return_param(1,0,{},'支付成功')

    def sn_pay_notify_person(self,id,uid_used,sn_id):
        sn_out_trade_num = self.create_out_trade_num() + '_'
        try:
            self.db.execute("UPDATE fs_user_event SET out_trade_no=%s,checkstatus=1 WHERE ueid=%s",sn_out_trade_num,id)
            self.db.execute("UPDATE fs_invite_sn SET uid_used=%s,is_used=1,use_time=%s WHERE id=%s",uid_used,int(time.time()),sn_id)
        except:
            return False
        return True

    def sn_pay_notify_group(self,id,uid_used,sn_id):
        """
         the input id is the ueid and if the sn is valid ,then there fun is used to creat_order_sn and set the checkstatus as in process
        """
        sn_out_trade_num = self.create_out_trade_num() + '_'
        ueid_list = self.get_group_attend_mem(id)
        ueid_str =  '(' + ','.join(ueid_list) + ')'
        if ueid_list is False:
            return False
        try:
            sql = "UPDATE fs_user_event SET out_trade_no='%s',checkstatus=1 WHERE ueid in %s" % (sn_out_trade_num,ueid_str)
            self.db.execute(sql)
            self.db.execute("UPDATE fs_invite_sn SET uid_used=%s,is_used=1,use_time=%s WHERE id=%s",uid_used,int(time.time()),sn_id)
        except:
            return False 
        return True

    def check_sn_valid(self,sn,eid):
        try:  user_sn_info = self.db.get("SELECT * FROM fs_invite_sn WHERE sn=%s  and eid=%s and is_used=0 and status=0",sn,eid)
        except Exception,e: self.treat_except(e)
        if user_sn_info is None:  return 1  # the sn is wrong  or it is used 
        expires = user_sn_info['expires']
        if int(time.time()) > expires:  return 2 #expires 
        return user_sn_info

class ScoreHandler(BaseHandler):
    def get_score_list(self,uid):
        try: score_list = self.find_some('fs_user_event',['escore','eusername','gid','bonus','ueid','eid','group_id'],uid=uid,status=0,escore={'rule':'<>','value':''})
        except Exception,e: self.treat_except(e)
        return score_list

    def get(self):
        action = self.get_argument('action')
        if action == 'get_score_list':
            uid = self.get_argument('uid')
            #so there may have user's group score and the personal score ,this all depend on the event type 
            score_list = self.get_score_list(uid)
            for index,score_info in enumerate(score_list):
                game_info = self.get_game_info(score_info['gid'],['gname','gfrontpage'])
                ename = self.get_full_event_name(score_info['eid'])
                score_list[index]['ename'] = ename
                score_list[index]['id'] = score_list[index]['ueid']
                score_list[index]['gfrontpage'] = options.ipnet + game_info['gfrontpage']
                score_list[index]['gname'] = game_info['gname']
                score_list[index]['escore'] = 'num ' + score_info['escore']
                score_list[index]['score_show_url'] = options.ipnet + '/py/score?action=show_event_score&eid=' + str(score_info['eid'])
                if int(score_info['group_id']):
                    score_list[index]['is_group'] = 1
                    score_list[index]['attend_info'] = self.get_group_info(score_info['group_id'])['group_name']
                else:
                    score_list[index]['is_group'] = 0
                    score_list[index]['attend_info'] = score_info['eusername']
            self.return_param(1,0,score_list,'成功')

        elif action == 'show_event_score':
            eid = self.get_argument('eid')
            self.out('is in develop yinshuai')

class GamemoreHandler(BaseHandler):

    def get(self):
        action = self.get_argument('action')
        if action == 'get_game_brief':
            gid = self.get_argument('gid')
            self.render('game_brief' + gid + '.html')

class UserHandler(BaseHandler):
    
    def get_current_day(self):
        return time.strftime("%Y-%m-%d",time.localtime(time.time()))
    def get_current_day_2(self):
        return time.strftime("%Y%m%d",time.localtime(time.time()))

    def post_api(self,url,type,**data_send):
        data=urllib.parse.urlencode(data_send)  
        return data_send

    def get(self):
        action = self.get_argument('action')
        if action == 'submit_health_data':
            a_d = self.get_multi_argument(['step_count','flights_climb','walk_run_distance','uid'])
            date_today = self.get_current_day()
            today_exist = self.find_db_sum('fs_health',rundate=date_today,uid=a_d['uid'])
            if not today_exist: self.insert_into_db('fs_health',self.treat_ar_dict(a_d,[],rundate=date_today)) 
            else: self.update_db('fs_health',a_d,{'uid':a_d['uid'],'rundate':date_today})
            self.return_param(1,0,{},'成功')

        elif action == 'get_user_info':
            a_d = self.get_multi_argument(['token','uid'])
            self.check_token_available(uid,a_d['token'])
            user_info = self.find_one('fs_users',['nickname','sex','assoc','height','weight','birthday','aposition','username','blood','idcard','email','tel_address','zipcode','area','emer_name','emer_tel'],uid=a_d['uid'])
            self.return_param(1,0,user_info,'success')

        elif action == 'submit_user_info':
            a_d = self.get_multi_argument(['token','uid'])
            self.check_token_available(uid,a_d['token'])
            change_param = self.get_multi_argument(['nickname','sex','height','assoc','weight','birthday','aposition','username','blood','idcard','email','tel_address','zipcode','area','emer_name','emer_tel'])
            self.update_db('fs_users',change_param,{'uid':a_d['uid']})
            self.return_param(1,0,{},'success')

        elif action == 'change_password':
            a_d = self.get_multi_argument(['uid','ori_password','new_password',{'token':False,'version':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
            password = self.get_userinfo_via_search_param('password',a_d['uid'])
            if a_d['ori_password'] != password: self.return_param(0,200,{},'ori password is not right')
            self.update_db('fs_users',{'password':a_d['new_password']},{'uid':a_d['uid']})
            if self.cacheRedis.exists('users:uid:' + a_d['uid']):
                self.cacheRedis.hset('users:uid:' + a_d['uid'],'password',a_d['new_password'])
            self.return_param(1,0,{},'成功')

    def post(self):
        action = self.get_argument('action')
        if action == 'change_password':
            a_d = self.get_multi_argument(['uid','ori_password','new_password',{'token':False,'version':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
            password = self.get_userinfo_via_search_param('password',a_d['uid'])
            if a_d['ori_password'] != password: self.return_param(0,200,{},'ori password is not right')
            self.update_db('fs_users',{'password':a_d['new_password']},{'uid':a_d['uid']})
            if self.cacheRedis.exists('users:uid:' + a_d['uid']):
                self.cacheRedis.hset('users:uid:' + a_d['uid'],'password',a_d['new_password'])
            self.return_param(1,0,{},'成功')


class PointHandler(BaseHandler):
    
    def get_y2i(self,timestamp):
        return time.strftime("%y-%m-%d %H:%M",time.localtime(int(timestamp)))

    def get_user_point_list(self,uid):
        try:  user_point_list = self.db.query("SELECT fp.time,fp.point_num,p.name FROM fs_point_from  AS fp LEFT JOIN fs_point AS p ON fp.pid=p.id WHERE fp.status=0 and fp.uid=%s order by fp.id desc",uid)
        except Exception,e: self.treat_except(e)
        for index,value in enumerate(user_point_list):  user_point_list[index]['time'] = self.get_y2i(value['time'])
        return user_point_list

    def get(self):
        action = self.get_argument('action')
        if action == 'get_point_page_url':
            uid = self.get_argument('uid')
            url_app = options.ipnet + '/py/point?action=get_point_page&uid=' + uid
            url_wecha = options.ipnet + '/ky/point?action=get_point_page&uid=' + uid
            return_dict = {'url_app':url_app,'url_wecha':url_wecha}
            self.return_param(1,0,return_dict,'成功')
        elif action == 'get_point_page':
            uid = self.get_argument('uid')
            str_show = "你好id为 %s 的用户，该功能正在开发中" % (uid)
            self.write(str_show)
        elif action == 'get_person_point_page':
            uid = self.get_argument('uid')
            user_point_list = self.get_user_point_list(uid)
            self.render('person_point.html',user_point_list=user_point_list)
        elif action == 'get_sum_point':
            uid = self.get_argument('uid')

class GroupHandler(BaseHandler):
    def decr_group_num(self,group_id):
        group_id = str(group_id)
        try:
            self.db.execute("UPDATE fs_group set membernum = membernum -1 where id =%s",group_id) 
            if self.cacheRedis.exists('group:id:' + group_id):
                self.cacheRedis.hincrby('group:id:' + group_id,'membernum',-1)
        except Exception,e: self.treat_except(e)
        return True
    def get(self):
         action = self.get_argument('action')
         if action == 'get_group_info':#get the all group info 
             group_id = self.get_argument('id')
             group_info = self.get_group_info(group_id)
             self.return_param(1,0,group_info,'成功')#return the data
         elif action == 'get_tag':
              tag_id = self.get_argument('tag_id')
              self.out(self.get_tag_info(tag_id))
         elif action == 'get_detail_group_info':#get more info include group_mem and group_mem_rank and my rank 
             a_d = self.get_multi_argument(['id','uid'])
             group_info = self.get_group_info(a_d['id']) 
             user_list_all = self.get_group_user_list(a_d['id'])
             user_info_all = [] 
             for uid in user_list_all: user_info_all.append(self.get_userinfo_via_search_param(['avatar','username','point'],uid))
             user_info_some_return = user_info_all[:int(options.mem_num_show)]
             user_info_point_all_return =  self.sort_by_param(user_info_all,'point',True)
             self.add_rank_string(user_info_point_all_return)
             return_dict = {} 
             return_dict['group_info'] = group_info
             return_dict['user_info_some_return'] = user_info_some_return
             return_dict['user_info_point_some_return'] = user_info_point_all_return[:int(options.mem_point_show_num)]
             for user_rank in user_info_point_all_return:
                 if user_rank['uid'] == a_d['uid']:
                     return_dict['my_rank'] = user_rank
                     break
             self.return_param(1,0,return_dict,'成功')

         elif action == 'get_all_group': #get my group list 
             """
             mygroup:uid:xxx  is the link of the group which i am in but not i created  
             leadergroup:uid:xxx  is the link of the group of my created 
             """
             uid = str(self.get_argument('uid'))
             group_info_return = []  #other man's group  
             leader_group_info_return = [] #the group of me 
             if not self.cacheRedis.exists('mygroup:uid:' + uid):
                group_id_list_db = self.db.query("SELECT group_id FROM fs_group_mem  WHERE uid = %s and is_leader=0",uid)
                for value in group_id_list_db:
                    self.cacheRedis.lpush('mygroup:uid:' + uid,value['group_id'])
             group_id_list = self.cacheRedis.lrange('mygroup:uid:' + uid,0,-1) 
             for group_id in group_id_list:
                 group_info_return.append(self.get_group_info(group_id))
             if not self.cacheRedis.exists('leadergroup:uid:' + uid):
                 group_id_list_db = self.db.query("SELECT group_id FROM fs_group_mem  WHERE uid = %s and is_leader=1",uid)
                 for value in group_id_list_db:
                     self.cacheRedis.lpush('leadergroup:uid:' + uid,value['group_id'])   
             leader_group_id_list = self.cacheRedis.lrange('leadergroup:uid:' + uid,0,-1)
             for group_id in leader_group_id_list:
                 leader_group_info_return.append(self.get_group_info(str(group_id)))

             invite_list = self.db.query("SELECT group_id,id AS invite_id FROM fs_invite WHERE uid = %s",str(uid))
             invite_info_return = []
             for invite_info in invite_list:
                 info_return = self.get_group_info(invite_info['group_id'])
                 info_return['invite_id'] = invite_info['invite_id']
                 invite_info_return.append(info_return)
             return_dict = {} 
             return_dict['group_info_return'] = group_info_return
             return_dict['leader_group_info_return'] = leader_group_info_return
             return_dict['group_num'] = len(group_info_return) + len(leader_group_info_return)
             return_dict['invite_list_return'] = invite_info_return
             # return_dict['apply_list_return'] = apply_list_return
             self.return_param(1,0,return_dict,'成功')

         elif action == 'get_group_list': 
             a_d = self.get_multi_argument([{'version':False,'page':False}])
             sql = 'SELECT g.createtime,g.id,g.group_name,g.intro,g.membernum,t.name AS tag_name,g.sumrun,g.avatar FROM fs_group AS g left join fs_tag AS t on t.id=g.tag_id' + \
                       ' WHERE g.status=0 ORDER BY g.id desc '
             if a_d.has_key('version') and  a_d['version'] == options.token_request_more_version:
                 sql = sql + " LIMIT %s,%s"  % ((int(a_d['page'])-1)*int(options.group_show_num),options.group_show_num)
             all_group_db = self.db.query(sql)
             for index,group_info in enumerate(all_group_db):
                 all_group_db[index]['createtime'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(group_info['createtime']))
                 all_group_db[index]['avatar'] = options.ipnet + str(group_info['avatar'])
             self.return_param(1,0,all_group_db,'成功')

         elif action == 'get_group_find':
             a_d = self.get_multi_argument(['find_name',{'version':False,'page':False}])
             sql = 'SELECT g.id,g.createtime,g.group_name,g.intro,g.membernum,t.name AS tag_name,g.sumrun,g.avatar FROM fs_group AS g left join fs_tag AS t on t.id=g.tag_id'
             sql = sql + " WHERE g.group_name like '%%" + a_d['find_name'] + "%%'" + " OR g.id='" + a_d['find_name'] + "' ORDER BY g.id desc"
             if a_d.has_key('version') and  a_d['version'] == options.token_request_more_version: 
                 sql = sql + " LIMIT %s,%s"  % ((int(a_d['page'])-1)*int(options.group_show_num),options.group_show_num)
             some_group_db = self.db.query(sql)
             for index,group_info in enumerate(some_group_db):
                 some_group_db[index]['createtime'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(group_info['createtime']))
                 some_group_db[index]['avatar'] = options.ipnet + str(group_info['avatar'])
             self.return_param(1,0,some_group_db,'成功')

         elif action == 'exit_group':#exit a group (the leader of the group if not you )
             a_d = self.get_multi_argument(['uid','id',{'version':False,'token':False}])
             if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # for that there is no  uid 
             self.update_db('fs_group_mem',{'status':1},{'group_id':a_d['id'],'uid':a_d['uid']})
             self.cacheRedis.lrem('group_user_list:group_id:' + a_d['id'],a_d['uid'])
             self.cacheRedis.lrem('mygroup:uid:' + a_d['uid'],a_d['id'])
             self.decr_group_num(a_d['id'])
             self.return_param(1,0,{},'成功')

         elif action == 'break_group': #break up a group  you are  the leader of the group 
             a_d = self.get_multi_argument(['uid','id',{'version':False,'token':False}])
             if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
             self.update_db('fs_group',{'status':1},{'id':a_d['id']})
             if self.cacheRedis.exists('leadergroup:uid:' + a_d['uid']):  self.cacheRedis.lrem('leadergroup:uid:' + a_d['uid'],a_d['id'])
             group_uid_list =  self.get_group_user_list(a_d['id'])      
             for uid in group_uid_list: self.cacheRedis.lrem('mygroup:uid:' + a_d['uid'],a_d['id'])
             if self.cacheRedis.exists('group_user_list:group_id:' + a_d['id']):  self.cacheRedis.delete('group_user_list:group_id:' + a_d['id'])   
             self.update_db('fs_group_mem',{'status':1},{'group_id':a_d['id']})
             self.return_param(1,0,{},'成功')

         elif action == 'show_all_members':
             group_id = str(self.get_argument('id'))
             group_user_list = self.get_group_user_list(group_id)
             mem_return = []
             for uid in group_user_list:
                 mem_return.append(self.get_userinfo_via_search_param(['username','avatar'],uid))
             self.return_param(1,0,mem_return,'成功')


         elif action == 'show_all_rank':
             group_id = str(self.get_argument('id'))
             user_list_all = self.get_group_user_list(group_id)
             user_info_all = []
             search_param = ['avatar','username','point']
             for uid in user_list_all:
                 user_info_all.append(self.get_userinfo_via_search_param(search_param,uid))
             #get user info order by user point ,fetch  mem_point_show_num
             user_info_point_return = []
             user_info_point_return =  self.sort_by_param(user_info_all,'point',True)
             self.add_rank_string(user_info_point_return)              #add rank string 
             self.return_param(1,0,user_info_point_return,'成功')
         else:
             pass  

    def post(self):
          action = self.get_argument('action')
          if action == 'create_group':   #create a new group 
              a_d = self.get_multi_argument(['uid','group_name','group_intro','group_tag_id',{'token':False,'version':False}])
              if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # of if the leader of the group is that man ?? 
              group_info = {'group_name':a_d['group_name'],'intro':a_d['group_intro'],'leader_id':a_d['uid'],'tag_id':a_d['group_tag_id'],'membernum':1,'createtime':int(time.time())}
              group_id = self.insert_into_db('fs_group',group_info)
              self.insert_into_db('fs_group_mem',{'group_id':group_id,'is_leader':1,'attendtime':int(time.time()),'uid':a_d['uid']})
              if self.cacheRedis.exists('leadergroup:uid:'+ a_d['uid']):self.cacheRedis.lpush('leadergroup:uid:' + a_d['uid'],group_id)
              self.return_param(1,0,{'id':group_id},'成功')

          elif action == 'change_param':
              a_d = self.get_multi_argument(['param','id',{'token':False,'version':False,'uid':False}])
              if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # of if the leader of the group is that man ?? 
              if a_d['param'] == 'groupname': 
                  new_groupname = self.get_argument('new_groupname')
                  self.update_db('fs_group',{'group_name':new_groupname},{'id':a_d['id']})
                  if self.cacheRedis.exists('group:id:' + a_d['id']): self.cacheRedis.hset('group:id:' + a_d['id'],'group_name',new_groupname)
                  self.return_param(1,0,{},'成功')
              elif a_d['param'] == 'group_intro': #change the group intro
                  new_group_intro = self.get_argument('new_group_intro')
                  self.update_db('fs_group',{'intro':new_group_intro},{'id':a_d['id']})
                  if self.cacheRedis.exists('group:id:' + a_d['id']): self.cacheRedis.hset('group:id:' + a_d['id'],'intro',new_group_intro)
                  self.return_param(1,0,{},'成功')
              else: pass


class InviteHandler(BaseHandler):

    def judge_alreay_send_invite(self,uid,group_id):
        return True if self.find_db_sum('fs_invite',group_id=group_id,uid=uid)  else False

    def judge_alreay_in_group(self,uid,group_id):
        return True if self.find_db_sum('fs_group_mem',group_id=group_id,uid=uid) else False

    def get(self):
        a_d = self.get_multi_argument(['action','id',{'version':False,'token':False,'uid':False}])
        if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # for that there is no  uid 
        if a_d['action'] == 'pass_invite':
            invite_info = self.find_one('fs_invite',['uid','group_id'],id=a_d['id'])
            self.insert_into_db('fs_group_mem',{'group_id':invite_info['group_id'],'uid':invite_info['uid'],'attendtime':int(time.time())})
            self.update_db('fs_group',{'membernum':1},{'id':invite_info['group_id']},'add')
            if self.cacheRedis.exists('group_user_list:group_id:' + str(invite_info['group_id'])):
                self.cacheRedis.rpush('group_user_list:group_id:' + str(invite_info['group_id']),str(invite_info['uid']))
            if self.cacheRedis.exists('mygroup:uid:' + str(invite_info['uid'])):self.cacheRedis.lpush('mygroup:uid:' + str(invite_info['uid']),str(invite_info['group_id']))
            if self.cacheRedis.exists('group:id:' + str(invite_info['group_id'])): self.cacheRedis.hincrby('group:id:' + str(invite_info['group_id']),'membernum',1)
            group_name = self.get_group_info(invite_info['group_id'])['group_name']
            userinfo = self.get_userinfo_via_search_param(['username','tel'],str(invite_info['uid']))
            self.update_db('fs_invite',{'status':1},{'id':a_d['id']})
            content = "(%s)(%s) 已经通过了你的 '%s'团队邀请" % (userinfo['username'],userinfo['tel'],group_name)
            self.send_sysinfo(invite_info['uid'],content,'好友通过邀请')
            self.return_param(1,0,{},'成功') 

        elif a_d['action'] == 'refuse_invite':
            self.update_db('fs_invite',{'status':1},{'id':a_d['id']})
            self.return_param(1,0,{},'成功')
        else: pass

    def post(self):
        action = self.get_argument('action')
        if action == 'invite_friends':
            a_d = self.get_multi_argument(['id','tel',{'version':False,'token':False,'uid':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) 
            uid = self.get_uid_via_tel(a_d['tel'])
            if not uid: return self.return_param(0,200,{},'该用户还没有注册')
            if self.judge_alreay_send_invite(uid,a_d['id']): return self.return_param(0,201,{},'邀请已发送，等待对方同意')
            if self.judge_alreay_in_group(uid,a_d['id']):  return self.return_param(0,202,{},'该用户已经在团队内')
            self.insert_into_db('fs_invite',{'group_id':a_d['id'],'uid':uid,'invitetime':int(time.time())})
            self.return_param(1,0,{},'成功')
  
class OrgHandler(BaseHandler):  #yinshuai
    def get(self):
        action = self.get_argument('action')
        if action == 'get_org': # search the organizition
            word = self.get_argument('word')
            self.return_param(1,0,self.find_some('fs_org',['username AS name'],username={'rule':'LIKE','value':'%%' + word + '%%'}),'success')


class NotifyHandler(BaseHandler):
    """wecha notify """
    def get(self):
        action = self.get_argument('action')
        if action == 'get_attend_info':
            attend_info = self.get_attend_info(self.get_argument('id'))
            event_info = self.get_event_info(attend_info['eid'])
            if int(attend_info['group_id']):#group_attend
                mem_num = self.find_db_sum('fs_user_event',out_trade_no=attend_info['out_trade_no'])
                self.return_param(1,0,{'ename':event_info['ename'],'epayfee':event_info['epayfee']*mem_num,'out_trade_no':attend_info['out_trade_no']},'success')
            else:#person attend
                self.return_param(1,0,{'ename':event_info['ename'],'epayfee':event_info['epayfee'],'out_trade_no':attend_info['out_trade_no']},'success')

        elif action == 'weipay_notify':
            out_trade_no = self.get_argument('out_trade_no')
            if out_trade_no[0:1] == 'a': self.update_db('fs_user_assoc',{'checkstatus':1},{'out_trade_no':out_trade_no})
            else: self.update_db('fs_user_event',{'checkstatus':1},{'out_trade_no':out_trade_no})

class ScienceHandler(RankHandler):
    science_step = [0,2999,5000,7000,9000,11000,13000,15000,20000]#right and left is all in 
    science_duration = [0,0,1800,2400,3000,3600,4200,5400,6000,7200] #for that the struturee is same, so use sort is a good way  second  only left
    science_point =[0,0,200,400,600,1000,800,600,400,200]

    def calc_science_point(self,user_step,user_duration):
        science_step = copy.deepcopy(self.science_step) #deep copy 
        science_step.append(user_step)
        step_rank = sorted(science_step).index(user_step)
        if step_rank < 2 or step_rank == 9  : return 0 #if the rank is 9 ,it means step chaoguo max step so 0 point is given
        return 2*self.science_point[step_rank] if user_duration >= self.science_duration[step_rank] and user_duration < self.science_duration[step_rank+1] else self.science_point[step_rank]

    def get(self):
        action = self.get_argument('action')
        if action == 'give_point_early_night':#every time ,fetch out 20 data and treat this 20 data  and then next
            date_str_info = time.strftime("%y%m%d",time.localtime(int(time.time())))
            runday_info = self.find_some("fs_sumrun_day",['*'],time=date_str_info,status=0)
            eid = eval(self.get_game_only_level_event(5))[0]
            for run_info in runday_info:
                if self.check_have_attend_by_uid(run_info['uid'],eid):
                    user_point_get = self.calc_science_point(run_info['step'],run_info['duration'])
                    if not user_point_get: continue #if the point is 0 then skip 
                    self.give_point(run_info['uid'],user_point_get)#add point to sum point
                    self.write_user_point_from(run_info['uid'],2,5,user_point_get)


class ApplyHandler(BaseHandler): #shenqing
    def get(self):
        action = self.get_argument('action')
        if action == 'pass_apply':#pass user apply  not used 
             a_d = self.get_multi_argument(['id'])
             apply_info = self.find_one('fs_group_apply',['uid','group_id'],id=a_d['id'])
             self.insert_into_db('fs_group_apply',{'group_id':apply_info['group_id'],'uid':apply_info['uid'],'attendtime':int(time.time())})
             if self.cacheRedis.exists('group_user_list:group_id:' + group_id): self.cacheRedis.rpush('group_user_list:group_id:' + group_id,uid)
             if self.cacheRedis.exists('mygroup:uid:' + uid): self.cacheRedis.lpush('mygroup:uid:' + uid,group_id)
             self.update_db('fs_group_apply',{'status':1},{'id':a_d['id']})
             self.return_param(1,0,{},'成功')

        elif action == 'refuse_apply':#refuse the apply not used 
            apply_id = self.get_argument('id')
            try: self.db.execute('DELETE FROM fs_group_apply WHERE id = %s',str(apply_id))
            except Exception,e: self.treat_except(e)
            self.return_param(1,0,{},'成功')
        else: pass

    def post(self):
        action = self.get_argument('action')
        if action == 'post_apply':
            a_d = self.get_multi_argument(['id','uid',{'version':False,'token':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
            leader_id = self.get_group_info(a_d['id'])['leader_id']
            if self.alreay_in_group(a_d['uid'],a_d['id']): return self.return_param(0,201,{},'你已经在该团队中')
            if self.add_user_to_group(a_d['uid'],a_d['id']): return self.return_param(1,0,{},'加入成功')
       

class LoginHandler(BaseHandler):

      def get(self):
          a_d = self.get_multi_argument(['version','tel','password'])
          if a_d['version'] == options.token_request_more_version:
              if not self.find_db_sum('fs_users',tel=a_d['tel']):  return self.return_param(0,0,{},'not register')
              user_info = self.find_one('fs_users',['password','uid','login_times'],tel=a_d['tel'])
              if not user_info['password'] == a_d['password']: return self.return_param(0,1,{},'wrong password')
              token = self.create_token(user_info['uid'])
              change_param = {'token':token,'login_times':user_info['login_times']+1,'last_login':int(time.time())}
              self.update_db('fs_users',change_param,{'tel':a_d['tel']})
              if self.cacheRedis.exists('users:uid:' + str(user_info['uid'])): self.cacheRedis.hmset('users:uid:' + str(user_info['uid']),change_param)
              self.return_param(1,0,{'token':token,'uid':user_info['uid']},'login success')

class LogoutHandler(BaseHandler):

    def clear_user_cache(self,uid):
        try:
            if self.cacheRedis.exists('users:uid:' + str(uid)):
                self.cacheRedis.delete('users:uid:' + str(uid))  
        except Exception,e: self.treat_except(e)


    def get(self):
        a_d = self.get_multi_argument(['uid','action','token'])
        if a_d['action'] == 'logout':
            self.check_token_available(a_d['uid'],a_d['token'])
            self.clear_user_cache(a_d['uid'])
            self.update_db('fs_users',{'token':''},{'uid':a_d['uid']})
            self.return_param(1,0,{},'success')

class SystemHandler(BaseHandler):
    #get system info such as the user has pass you invite 
    def get(self):
        action = self.get_argument('action')
        if action == 'get_sysinfo':
            uid = self.get_argument('uid')
            try:
                sysinfo_list = self.db.query("SELECT * FROM fs_sysinfo WHERE uid = %s and status=0 order by id desc",uid)
                for index,sysinfo in enumerate(sysinfo_list):
                    sysinfo['time'] = time.strftime("%Y-%m-%d %H:%M",time.localtime(sysinfo['time']))
                    sysinfo_list[index] = sysinfo
            except Exception,e: self.treat_except(e)
            self.return_param(1,0,sysinfo_list,'成功')

        elif action == 'del_sysinfo':
            id = self.get_argument('id')
            try: self.db.execute("DELETE FROM fs_sysinfo WHERE id = %s",id)
            except Exception,e: self.treat_except(e)
            self.return_param(1,0,{},'成功')

        elif action == 'get_ad': #get the picList of the add
            if not self.cacheRedis.exists('ad_pic'):
                try:
                    picList = self.db.query("SELECT * FROM fs_ad")
                    for index,value in enumerate(picList):
                        value['pic'] = options.ipnet + value['pic']
                        picList[index] = value
                    self.cacheRedis.set('ad_pic',picList)
                except Exception,e: self.treat_except(e)
            picList = self.cacheRedis.get('ad_pic')
            self.return_param(1,0,eval(picList),'成功')

class TagHandler(BaseHandler):
    def get(self):
       if not self.cacheRedis.exists('tag_all'):
           tag_all_db = self.db.query("SELECT * FROM fs_tag")
           for index,tag in enumerate(tag_all_db):
               tag_all_db[index]['pic'] = options.ipnet + '/Uploads/TagPic/' + tag['pic']
           self.cacheRedis.set('tag_all',tag_all_db)
       tag_all = self.cacheRedis.get('tag_all')
       self.return_param(1,0,eval(tag_all),'成功')

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
