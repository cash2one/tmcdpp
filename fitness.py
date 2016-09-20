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
from Models.postmodel import PostModel
from Models.systemmodel import SystemModel
from Models.tagmodel import TagModel
from Models.admodel import AdModel
from Models.groupmodel import GroupModel
from Models.groupmemmodel import GroupMemModel
from Models.invitemodel import InviteModel
from Models.wechausermodel import WechaUserModel
from Common.commonfunc import CommonFunc
from Models.interactmodel import InteractModel
from Models.pointordermodel import PointOrderModel
from Models.usereventmodel import UserEventModel
from Models.rundatamodel import RunDataModel
from Models.livemodel import LiveModel
from Models.scoremodel import ScoreModel
from Models.gamemodel import GameModel
from Models.runcommunitymodel import RunCommunityModel
from Models.organizationinfomodel import OrganizationInfoModel
from Models.organizationapplymodel import OrganizationApplyModel
from Models.mongotestmodel import MongoTestModel
from Models.musermodel import MUserModel
from Controller.notecontroller import NoteController
from Controller.fcircontroller import FCirController
from Controller.sharecontroller import ShareController
from Controller.followcontroller import FollowController
from Controller.usercontroller import UserController
from Controller.rcomcontroller import RCommController
from Controller.gamecontroller import GameController
from Controller.orgclubcontroller import OrgClubController
from Controller.actcontroller import ActController
from Models.notemodel import NoteModel
from Models.notecommodel import NoteComModel
from Func.publicfunc import PublicFunc

reload(sys)
sys.setdefaultencoding('utf8')
settings = {'debug':True}
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/[pk]y/tag", TagHandler),
            (r"/base",BaseHandler),
            (r"/[pk]y/test",TestHandler),
            (r"/[pk]y/test1",Test1Handler),
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
            (r"/[pk]y/third",ThirdHandler),
            (r"/[pk]y/bind",BindHandler),
            (r"/[pk]y/interact",InteractHandler),
            (r"/[pk]y/adminsend",AdminSendHandler),
            (r"/[pk]y/duiba",DuibaHandler),
            (r"/[pk]y/comm",CommHandler),
            # (r"/[pk]y/commrank",CommRankHandler),
            (r"/[pk]y/reward",RewardHandler),
            (r"/[pk]y/false",FalseHandler),
            (r"/[pk]y/notepub",NotePubHandler),
            (r"/[pk]y/notepri",NotePriHandler),
            (r"/[pk]y/notecommpub",NoteCommPubHandler),
            (r"/[pk]y/notecommpri",NoteCommPriHandler),
            (r"/[pk]y/postpri",PostPriHandler),
            (r"/[pk]y/postpub",PostPubHandler),
            (r"/[pk]y/postlovepub",PostLovePubHandler),
            (r"/[pk]y/postlovepri",PostLovePriHandler),
            (r"/[pk]y/actpub",ActPubHandler),
            (r"/[pk]y/actpri",ActPriHandler),
            (r"/[pk]y/share",ShareHandler),
            (r"/[pk]y/orgpri",OrgPriHandler),
            (r"/[pk]y/orgpub",OrgPubHandler),
            (r"/[pk]y/followpub",FollowPubHandler),
            (r"/[pk]y/userevent",UserEventHandler),
            (r"/[pk]y/adver",AdverHandler)


        ]
        settings = dict(
            blog_title=u"fitness",
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
        self.usersmodel = UsersModel()
        self.groupmodel = GroupModel()
        self.tagmodel = TagModel.get_instance()
        self.invitemodel = InviteModel()
        self.systemmodel = SystemModel.get_instance()
        self.admodel = AdModel.get_instance()
        self.groupmodel = GroupModel.get_instance()
        self.groupmemmodel = GroupMemModel.get_instance()
        self.wechausermodel = WechaUserModel.get_instance()
        self.interactmodel = InteractModel.get_instance()
        self.pointordermodel = PointOrderModel.get_instance()
        self.usereventmodel = UserEventModel.get_instance()
        self.rundatamodel = RunDataModel.get_instance()
        self.livemodel = LiveModel.get_instance()
        self.scoremodel = ScoreModel.get_instance()
        self.runcommunitymodel = RunCommunityModel.get_instance()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    @property
    def cacheRedis(self):
        return self.application.cacheRedis
    @property
    def usersmodel(self):
        return self.application.usersmodel
    @property
    def groupmodel(self):
        return self.application.groupmodel
    @property
    def tagmodel(self):
        return self.application.tagmodel
    @property
    def invitemodel(self):
        return self.application.invitemodel
    @property
    def systemmodel(self):
        return self.application.systemmodel
    @property
    def admodel(self):
        return self.application.admodel
    @property
    def groupmodel(self):
        return self.application.groupmodel
    @property
    def groupmemmodel(self):
        return self.application.groupmemmodel
    @property
    def wechausermodel(self):
        return self.application.wechausermodel
    @property
    def interactmodel(self):
        return self.application.interactmodel
    @property
    def pointordermodel(self):
        return self.application.pointordermodel

    @property 
    def usereventmodel(self):
        return self.application.usereventmodel
    @property
    def rundatamodel(self):
        return self.application.rundatamodel;
    @property
    def livemodel(self):
        return self.application.livemodel
    @property
    def scoremodel(self):
        return self.application.scoremodel
    @property
    def runcommunitymodel(self):
        return self.application.runcommunitymodel
    
    
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
        if not token_server or not token_client == token_server : return self.return_param(0,502,{},'您已经注销登录或者在其他地方登录，请重新登录')
        return True

    def get_multi_argument(self,argument_list):
        """ input a list of argument and it will result a list of dict"""
        dict_return = {}
        for param in argument_list: 
            try:
                if isinstance(param,dict):
                    for key in param: 
                        if param[key] is False :
                            try: dict_return[key] = self.get_argument(key).replace("'",'\'').replace('"','\"')
                            except:continue
                        else: dict_return[param] = self.get_argument(key,param[key]).replace("'",'\'').replace('"','\"')
                else: dict_return[param] = self.get_argument(param)
            # except Exception,e: self.treat_except(e)
            except Exception,e: raise
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

    def get_random(self,num):
        """get num random str"""
        return  ''.join(sample('abcdefghijklmnopqrstuvwxyz1234567890!',8))

    def treat_except(self,e):
        print e
        self.return_param(0,505,{},e) 

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
        except Exception,e: 
            raise
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
        status_name_dict = {'1':'审核中','2':'报名成功','3':'attend fail'}
        status_name_dict['0'] = '支付' if is_group  else '未支付'
        return status_name_dict[checkstatus]
        
    def get_user_attend_list(self,uid,info_list):
        return self.find_some('fs_user_event',info_list,uid=uid,status=0)

    def justify_user_attend(self,eid,idcard):
        try:  count = self.find_db_sum('fs_user_event',eidcard=idcard,eid=eid,status=0)
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
                        print self.check_have_attend_by_uid(user_info['uid'],eid)
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

   #template output data 
    def return_param(self,result,flag,data,desc):
        return_dict = {'result':result,'flag':flag,'data':data,'desc':str(desc)}
        self.write(return_dict)
        

    def return_param_switch(self,tuple_input):
        return_dict = {'result':tuple_input[0],'flag':tuple_input[1],'data':tuple_input[2],'desc':str(tuple_input[3])}
        self.write(return_dict)

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

    #get the userinfo of input param  the search_param may like username user_password etc or a list or a tuple 
    def get_userinfo_via_search_param(self,search_param,uid):
        uid = str(uid)
        # if not self.cacheRedis.exists('users:uid:' + uid):# if this user info is not exist then read from mysql and write to cache
        path = options.ipnet
        userinfo = self.db.get("SELECT username,password,tel,token,idcard,login_times,sex,nickname,last_login,CONCAT(%s,avatar) AS avatar,point FROM fs_users WHERE uid = %s",path,uid)
        return_info = {}
        if isinstance(search_param,str):
            return userinfo[search_param]

        else:
            for ele in search_param:
                return_info[ele] = userinfo[ele]
        return return_info

        if True:
            path = options.ipnet
            userinfo = self.db.get("SELECT username,password,tel,token,idcard,login_times,sex,nickname,last_login,CONCAT(%s,avatar) AS avatar,point FROM fs_users WHERE uid = %s",path,uid)
            self.cacheRedis.delete('users:uid:' + uid)
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

class Test1Handler(BaseHandler):
    def get(self):
        print self.db


class FalseHandler(BaseHandler):
    def get(self):
        false_uid = [x for x in xrange(3695,3795)]# uid from 3695 to 3794 
        comm_id_list  = ['5767d121e13823130724f086','5767d121e13823130724f087']
        # print random.choice(comm_id_list)
        # self.usersmodel.make_false_user_data() # 生成3695-3794  100条水军
        # self.runcommunitymodel.init_community() # init paotuan 
        # for uid in false_uid:
            # self.runcommunitymodel.attend_community(uid,random.choice(comm_id_list))



class TestHandler(BaseHandler):
    
    def get(self):
        # self.runcommunitymodel.add_interact(35,'caonimei','5767a64fe13823f4969a8c34')
        # d = self.runcommunitymodel.get_interact('5767a64fe13823f4969a8c34',0)
        # self.out(d)
        # 5767d121e13823130724f086
        # self.runcommunitymodel.update_run_data('5767d121e13823130724f086',3698,500,600)
        # print PublicFunc.get_date_info(1525896369,['year','month','day'])
        #check_token_avaiable 
        # print UsersModel().check_token_available(7,'dd')
        argu = self.get_argument('yin')
        self.write(argu)





 

        return 
        #       self.m_c.update({'_id':ObjectId(comm_id)},{'$inc':{'member_num':1},'$push':{'comm_member':member_dict}})
        MongoTestModel.get_instance().adding()
        return 
        li = []
        info = {'name':"yinshuai"}
        i = 10
        while i:
            i -=1 
            li.append(info)
        for my_info in li:
            my_info['name'] = "heheda"
            my_info['madan'] = "madan"
        self.out(li)
        #print self.usersmodel.judge_tel_bind_status('18811399881',35)
        # name = self.get_argument('name')
        # self.jbzmodel.person_attend()
        # self.write(len(str(name)))
        # if name == 'yinshuai' : self.write('equal')
        # print self.find_one('fs_users',['*'],uid=35)

        return 
        # return 


        print UsersModel().check_token_available(7,'dd')
        return 
        # d = self.db_ins.find_some('fs_tag',['*'])
        post = PostModel()
        post.my_insert()
        return 


        user = UsersModel()
        # d = user.get_uid_via_tel('18811399881')
        d = user.get_token(7)
        d = user.check_token_available(7,d)
        

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
            # if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # for that there is no  uid 
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
            if warn_str: return self.return_param(0,200,{},warn_str)
            have_attend = self.justify_user_attend(eid,userInfo['idcard'])
            if have_attend: return self.return_param(0,201,{},'用户已经报名了该项目')
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
            # if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: return self.check_token_available(a_d['uid'],a_d['token'])
            age = self.get_age_via_idcard(a_d['eidcard'])
            if self.justify_user_attend(a_d['eid'],a_d['eidcard']): return self.return_param(0,200,{},'你已经报名了该项目')
            available_sign = self.check_event_available(a_d['eid'],1)
            if available_sign is 1:  return self.return_param(0,201,{},'报名结束')
            if available_sign is 2:  return self.return_param(0,202,{},'该项目报名名额已满')
            data_write = self.treat_ar_dict(a_d,['token','version'],eage=age,attendtime=int(time.time()))
            user_avatar = self.get_userinfo_via_search_param(['avatar'],a_d['uid'])['avatar']
            data_write['picPath'] =   user_avatar[user_avatar.index('/Uploads'):] 
            event_info = self.get_event_info(a_d['eid'])
            epayfee = event_info['epayfee']
            ename = event_info['ename']
            game_info = self.get_game_info(a_d['gid'])
            gtype_id = int(game_info['gtype_id'])
            #if the game type if person not need payfee then we set the checkstatus 2 
            if not float(epayfee): data_write['checkstatus'] = 1 # the event is free
            if int(a_d['eid']) == 202: data_write['checkstatus'] = 2 # check pass,dont need checkout 
            else: data_write['out_trade_no'] = self.create_out_trade_num()
            if gtype_id in self.run_game_not_need_check_type: data_write['checkstatus'] = 2 #the type of the game dont need pay and dont need check
            pri_id = self.insert_into_db('fs_user_event',data_write)
            self.incr_game_attend_num(a_d['eid'],1)
            #send sms 
            if int(a_d['eid']) == 202:
                send_content = '%s,您好!恭喜您成功报名8月7日(周日)上午8:30在良乡体育中心举办的青创动力2016年科学健身运动项目推广活动，请您于8月5日下午两点到良乡体育中心综合馆领取服装。' % a_d['eusername']
                PublicFunc.send_sms(a_d['etel'],send_content)
            else:
                send_content = "%s,恭喜您成功报名 %s 赛事项目" % (a_d['eusername'],ename)
            # print send_content
            
            return self.return_param(1,0,{'id':pri_id},'报名表提交成功')

class MapHandler(BaseHandler):

    def get(self):
        a_d_head = self.get_multi_argument(['uid','version','token','action'])
        if a_d_head['version'] == options.token_request_more_version: self.check_token_available(a_d_head['uid'],a_d_head['token'])
        if a_d_head['action'] == 'get_run_belong':
            belong_sn = a_d_head['uid'] + str(self.get_current_timestamp())
            self.return_param(1,0,{'belong_sn':belong_sn},'success')
        # elif a_d_head['action'] == ''


class GameHandler(BaseHandler):

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

            game_list = GameController().get_game_list(uid)
            self.return_param(1,0,game_list,'成功')
       
        elif action == 'get_game_info':
            try:
                a_d_m = self.get_multi_argument(['gid','uid'])
                game_info = GameController().get_game_status(a_d_m['uid'],a_d_m['gid'])
                self.return_param(1,0,game_info,'成功')
            except Exception,e:
                return self.treat_except(e)

        elif action == 'rank_test':
            uidList = self.get_user_attend_event(8)
        elif action == 'get_recent_run':
            try:
                a_d = self.get_multi_argument(['gid'])
                if int(a_d['gid']) == 7: eid = 11 
                else: return self.out('目前只针对健步走活动开放')
                recent_run_man = self.rundatamodel.get_recent_run_man_single(eid)
                self.return_param(1,0,recent_run_man,'success')
            except Exception,e:self.treat_except(e)

        elif action == 'get_game_lives':
            try:
                gid = self.get_argument('gid')
                info = self.livemodel.get_live_list(gid)
                self.return_param(1,0,info,'success')
            except Exception,e:self.treat_except(e)

        elif action == 'get_game_score':
            try:
                gid = self.get_argument('gid')
                score_list = self.scoremodel.get_score_list(gid)
                return self.return_param(1,0,score_list,'success')
            except Exception,e:self.treat_except(e)

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
            lives_info_db = LiveModel().get_live_list(gid)
            self.return_param(1,0,lives_info_db,'成功')

class InteractHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'add_interact':
            try:
                a_d = self.get_multi_argument(['uid','content','comm_id'])
                self.interactmodel.add_interact(a_d['uid'],a_d['content'],a_d['comm_id'])
                self.return_param(1,0,{},'success')
            except Exception,e:self.treat_except(e) 
        elif action == 'get_interact':
            try:
                a_d = self.get_multi_argument(['comm_id','page'])
                interact_info = self.interactmodel.get_interact(a_d['comm_id'],a_d['page'])
                self.return_param(1,0,interact_info,'success')
            except Exception,e:self.treat_except(e)

        else: pass


class RankHandler(BaseHandler):
    type_table = {'day':'fs_person_rundata_day','week':'fs_person_rundata_week','month':'fs_person_rundata_month','quarter':'fs_person_rundata_quarter',\
                   'year':'fs_person_rundata_year'}
    type_group_table = {'day':'fs_group_rundata_day','week':'fs_group_rundata_week','month':'fs_group_rundata_month','quarter':'fs_group_rundata_quarter',\
                   'year':'fs_group_rundata_year'}
    time_local = time.localtime(int(time.time()))
    current_quarter = int(time.strftime("%m",time_local))/3###############################this place has problem
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
            print sql
            person_popular_list = self.db.query(sql)
            if not person_popular_list: return []
            self.cacheRedis.set("person_popular_" + type + ":eid:" + eid,person_popular_list,options.rank_data_expires)
        person_popular_list = eval(self.cacheRedis.get('person_popular_' + type + ':eid:' + eid))
        for index,user_popular_info in enumerate(person_popular_list):
            user_info = self.get_userinfo_via_search_param(['avatar','nickname'],user_popular_info['uid'])
            person_popular_list[index]['avatar'] = user_info['avatar']
            person_popular_list[index]['nickname'] = user_info['nickname'] if user_info['nickname'] else options.default_nick_name
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
            print person_popular_list
            ##这里还要取出更多的人，那些只要参加的人都取出来
            all_attend_man = UserEventModel().get_all_attend_man(eid)
            for user_info in all_attend_man:
                try:run_info = UsersModel().get_import_user_info(user_info['uid'],['avatar','nickname'])
                except:continue
                run_info['nickname'] = run_info['nickname'] if run_info['nickname'] else options.default_nick_name
                run_info['duration'] = '00:00:00'
                run_info['step'] = 0
                person_popular_list.append(run_info)

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
            attend_type = -1 if uid == '0' else UserEventModel().check_attend_type(uid,eid)
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

class CommHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'attend_comm': #加入走跑圈子 
            try:   
                # self.runcommunitymodel.init_community()
                a_d = self.get_multi_argument(['uid','comm_id'])
                if not int(a_d['uid']): return self.return_param(0,200,{},'您还没有登录，不能加入')
                gid = self.runcommunitymodel.get_game_comm_belong(a_d['comm_id'])
                if not gid: return self.return_param(0,200,{},'不存在该跑团')
                attend_comm_info = self.usereventmodel.check_have_attend_comm(a_d['uid'],gid)
                if attend_comm_info is None : return self.return_param(0,205,{},'您还没有报名该赛事')
                if attend_comm_info[0] is True: return self.return_param(0,201,{},'您已经加入了该赛事下的其他跑团！')
                self.runcommunitymodel.attend_community(a_d['uid'],a_d['comm_id'])
                self.usereventmodel.attend_comm(a_d['comm_id'],attend_comm_info[1])
                self.return_param(1,0,{},'加入成功')
            except Exception,e: 
                raise 
                self.treat_except(e)

        elif action == 'update_run_data':
            """更新跑团用户数据"""
            try:
                a_d = self.get_multi_argument(['uid','distance','duration'])
                attend_info = self.usereventmodel.check_have_attend_comm(a_d['uid'],7)
                if attend_info is None or attend_info[0] == False:return  #没有报名或者没有加跑团的返回
                comm_id = attend_info[1]
                self.runcommunitymodel.update_run_data(comm_id,a_d['uid'],a_d['distance'],a_d['duration'])
            except Exception,e:raise
            
        elif action == 'get_my_comm_info':
            try:
                a_d = self.get_multi_argument(['uid','comm_id'])#获取我所在的跑团的信息
                gid = self.runcommunitymodel.get_game_comm_belong(a_d['comm_id'])
                game_info = GameModel.get_instance().get_game_info(gid,['gstarttime','gendtime','gattend'])
                data_return = {'attend_num':game_info['gattend'],'start_date':PublicFunc.stamp_to_Ymd(game_info['gstarttime']),'end_date':PublicFunc.stamp_to_Ymd(game_info['gendtime'])}
                user_in_comm = self.runcommunitymodel.judge_user_in_comm(a_d['uid'],a_d['comm_id'])
                data_return['have_attend'] = 1 if user_in_comm else 0
                data_return['avatar'] = self.usersmodel.get_import_user_info(a_d['uid'],['avatar'])['avatar']
                if user_in_comm:
                    data_return['rank_event'] = 20
                    data_return['rank_g'] = 150
                self.return_param(1,0,data_return,'success')
            except Exception,e: self.treat_except(e)

        elif action == 'get_comm_rank':
            try:
                a_d = self.get_multi_argument(['comm_id','page'])
                rank_list_info = self.runcommunitymodel.get_community_rank(a_d['comm_id'],a_d['page'])
                self.return_param(1,0,rank_list_info,'success')
            except Exception,e:self.treat_except(e)


class UserEventHandler(BaseHandler):
    pass 

class DuibaHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'get_en_url':
            try:
                a_d = self.get_multi_argument(['token','uid'])
                if not a_d['uid'] == 'not_login ' and not self.usersmodel.check_token_available(a_d['uid'],a_d['token']): return self.return_param(0,200,{},'wrong token')
                credits = 0 if a_d['uid'] == 'not_login' else self.usersmodel.get_import_user_info(a_d['uid'],['point'])['point']
                url = PublicFunc.do_curl_get('http://101.200.214.68/duiba.php?action=get_url&uid=' + str(a_d['uid']) + '&credits=' + str(credits))
                self.return_param(1,0,url.replace("\t","").replace("\r","").replace("\n",""),'success')
            except Exception,e: self.treat_except(e)
        elif action == 'save_order':#保存订单数据
            try:
                a_d = self.get_multi_argument(['appKey','credits','timestamp','description','orderNum','uid'])
                user_point = self.usersmodel.get_import_user_info(a_d['uid'],['point'])['point']
                if user_point < a_d['credits']: self.return_param(0,200,{},'积分不足')
                bizid = self.pointordermodel.save_order(a_d)
                self.usersmodel.change_user_point(a_d['uid'],0-int(a_d['credits']))
                self.return_param(1,0,{'bizId':bizid},'success')
            except Exception,e: 
                self.return_param(0,200,{},e)
        elif action == 'order_notify':#订单回调
            try:
                a_d = self.get_multi_argument(['orderNum','success'])
                if self.pointordermodel.change_order_status(a_d['orderNum'],a_d['success']):
                    self.write('ok')
            except Exception,e: self.write('fail')
        else: pass

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
            if not self.usersmodel.check_token_available(a_d['uid'],a_d['token']):
                return self.return_param(0,200,{},'您已经注销登录或者在其他地方登录，请重新登录')
            user_info = self.find_one('fs_users',['nickname','sex','assoc','height','weight','birthday','aposition','username','blood','idcard','email','tel_address','zipcode','area','emer_name','emer_tel'],uid=a_d['uid'])
            self.return_param(1,0,user_info,'success')

        elif action == 'submit_user_info':
            try:
                a_d = self.get_multi_argument(['token','uid'])
                # self.check_token_available(a_d['uid'],a_d['token'])
                change_param = self.get_multi_argument([{'nickname':False},{'sex':False},{'height':False},{'assoc':False},{'weight':False},{'birthday':False},{'aposition':False},
                    {'username':False},{'blood':False},{'idcard':False},{'email':False},{'tel_address':False},{'zipcode':False},{'area':False},{'emer_name':False},{'emer_tel':False}])
                self.update_db('fs_users',change_param,{'uid':a_d['uid']})
                self.return_param(1,0,{},'提交成功')
            except Exception,e:
                print e

        elif action == 'change_password':
            a_d = self.get_multi_argument(['uid','ori_password','new_password',{'token':False,'version':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
            password = self.get_userinfo_via_search_param('password',a_d['uid'])
            if a_d['ori_password'] != password: self.return_param(0,200,{},'ori password is not right')
            self.update_db('fs_users',{'password':a_d['new_password']},{'uid':a_d['uid']})
            if self.cacheRedis.exists('users:uid:' + a_d['uid']):
                self.cacheRedis.hset('users:uid:' + a_d['uid'],'password',a_d['new_password'])
            self.return_param(1,0,{},'成功')

        elif action == 'person_center':
            try:
                a_d = self.get_multi_argument(['uid','version','action'])
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['other_uid'])
                    person_center = UserController().person_center(a_d['uid'],a_d_m['other_uid'])
                    self.return_param(1,0,person_center,'success')
            except Exception,e:
                raise
                self.treat_except(e)

        elif action == 'm_t_m':
            print FCirController().just_just()


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


class RewardHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'get_reward_list':
            try:
                a_d = self.get_multi_argument(['page'])
                reward_list =  self.pointordermodel.get_reward_list(a_d['page'])
                self.return_param(1,0,reward_list,'success')
            except Exception,e:self.treat_except(e)

 

class PointHandler(BaseHandler):

    def get_user_point_list(self,uid):
        try:  user_point_list = self.db.query("SELECT fp.time,fp.point_num,p.name FROM fs_point_from  AS fp LEFT JOIN fs_point AS p ON fp.pid=p.id WHERE fp.status=0 and fp.uid=%s order by fp.id desc",uid)
        except Exception,e: self.treat_except(e)
        for index,value in enumerate(user_point_list):  user_point_list[index]['time'] =  PublicFunc.stamp_to_YmdHM(value['time'])
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



class AdverHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['action'])
            return_data = {}
            if a_d['action'] == 'get_adver':
                return_data['html_url'] =  "http://101.200.214.68"
                return_data['pic_url'] = "http://101.200.214.68/Uploads/adver/front.jpg"
                self.return_param(1,0,return_data,'success');
            elif a_d['action'] == 'get_act_adver':
                return_list = []
                info['html_url'] = "http://www.baidu.com"
                info['pic_path'] = "http://101.200.214.68/Uploads/Picture/GamePic/2016-04-04/5702794c0a73f.jpg"
                return_list.append(info)
                info['html_url'] = "http://www.baidu.com"
                info['pic_path'] = "http://101.200.214.68/Uploads/Picture/GamePic/2016-08-29/57c3d1c432bfa.jpg"
                return_list.append(info)
                self.return_param(1,0,return_list,'success')
        except Exception,e:
            self.treat_except(e)

class NotePubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action'])
            if a_d['action'] == 'get_note_info':
                a_d_m = self.get_multi_argument(['note_id'])
                note_info = NoteController().get_note_info(a_d_m['note_id'])
                NoteController().update_see_num(a_d_m['note_id'])
                return_dict = {'note_basic_info':note_info[0],'note_comm_info':note_info[1]}
                self.return_param(1,0,return_dict,'success')

            elif a_d['action'] == 'get_note_list':
                a_d_m = self.get_multi_argument(['page'])
                note_list = NoteModel.get_instance().get_note_list(a_d_m['page'])
                return self.return_param(1,0,note_list,'success')

            elif a_d['action'] == 'get_user_note': #获取我的帖子
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['page'])
                    note_list = NoteController().get_user_note(a_d['uid'],a_d_m['page'])
                    return self.return_param(1,0,note_list,'success')
                    
            elif a_d['action'] == 'get_pic_list':
                if a_d['version'] >= '3.2':
                    pic_list = ['http://101.200.214.68/Uploads/add1.jpg','http://101.200.214.68/Uploads/add1.jpg','http://101.200.214.68/Uploads/add1.jpg']
                    pic_num = len(pic_list)
                    data_return = {'pic_num':pic_num,'pic_list':pic_list}
                    return self.return_param(1,0,data_return,'success')

        except Exception,e:
            self.treat_except(e)


class NotePriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','token','version','action'])
            if not UsersModel.get_instance().check_token_available(a_d['uid'],a_d['token']):
                pass
                # return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'release_note':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['title','content'])
                    note_id = NoteController().release_note(a_d['uid'],a_d_m['title'],a_d_m['content'])
                    return self.return_param(1,0,{"note_id":note_id},'发布成功')
        except Exception,e:
            self.treat_except(e)

    def post(self):
        try:
            a_d = self.get_multi_argument(['uid','token','version','action'])
            if not UsersModel.get_instance().check_token_available(a_d['uid'],a_d['token']):
                pass
                # return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'release_note':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['title','content'])
                    note_id = NoteController().release_note(a_d['uid'],a_d_m['title'],a_d_m['content'])
                    return self.return_param(1,0,{"note_id":note_id},'发布成功')
        except Exception,e:
            self.treat_except(e)


class NoteCommPubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action'])
            if a_d['action'] == 'get_comm_list': #获取评论分页列表
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['note_id','page'])
                    if not NoteController().judge_note_exist(a_d_m['note_id']): return self.return_param(0,200,{},options.note_not_exist)
                    comm_list = NoteController().get_note_comm(a_d_m['note_id'],a_d_m['page'])
                    self.return_param(1,0,comm_list,'success')
        except Exception,e:
            self.treat_except(e)

class NoteCommPriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','token','version','action'])
            if not UsersModel().check_token_available(a_d['uid'],a_d['token']): return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'make_comment': #评论帖子   
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['note_id','comm_content'])
                    if not NoteController().judge_note_exist(a_d_m['note_id']): return self.return_param(0,200,{},options.note_not_exist)
                    comm_id = NoteController().make_comment(a_d_m['note_id'],a_d['uid'],a_d_m['comm_content'])
                    return self.return_param(1,0,{'comm_id':comm_id},'成功')

            elif a_d['action'] == 'agree_comment':#为帖子的评论点赞
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['comm_id'])
                    if not NoteController().judge_comm_exist(a_d_m['comm_id']):return self.return_param(0,200,{},'不存在该条帖子回复')
                    result = NoteController().agree_comment(a_d['uid'],a_d_m['comm_id'])
                    if result == 'has_agree': self.return_param(0,200,{},'您已经点赞')
                    else: self.return_param(1,0,{},'点赞成功')

        except Exception,e: 
            self.treat_except(e)

class PostPubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action'])
            if a_d['action'] == 'get_post_info':#获取说说信息
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['post_id'])
                    if not FCirController().judge_post_exist(a_d_m['post_id']):return self.return_param(0,200,{},options.post_not_exist)
                    post_info = FCirController().get_post_info(a_d['uid'],a_d_m['post_id'])
                    self.return_param(1,0,post_info,'操作成功')

            elif a_d['action'] == 'get_comm_list':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['post_id','page'])
                    comm_list = FCirController().get_comm_list(a_d_m['post_id'],a_d_m['page'])
                    self.return_param(1,0,comm_list,'success')

            elif a_d['action'] == 'get_post_list':#获取说说列表,
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['page','uid'])
                    post_list = FCirController().get_post_list(a_d_m['uid'],a_d_m['page'])
                    self.return_param(1,0,post_list,'success')

            elif a_d['action'] == 'get_user_post':#获取我的朋友圈
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['page'])
                    post_list = FCirController().get_user_post(a_d['uid'],a_d_m['page'])
                    self.return_param(1,0,post_list,'sucess')
            elif a_d['action'] == 'get_recommend_list':
                if a_d['version'] >= '3.2':
                    re_list = FCirController().get_recommend_list(a_d['uid'])
                    self.return_param(1,0,re_list,'success')

            elif a_d['action'] == 'find_friends':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['nick_find','page','uid'])
                    # self.write(a_d_m)
                    friends_list = FCirController().find_friends(a_d_m['nick_find'],a_d_m['page'],a_d_m['uid'])
                    self.return_param(1,0,friends_list,'success')


        except Exception,e:
            self.treat_except(e)

class PostPriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','token','version','action'])
            if not UsersModel().check_token_available(a_d['uid'],a_d['token']): return self.return_param(0,200,{},'您已经注销登录或者在其他地方登录，请重新登录')
            if a_d['action'] == 'release_post':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument([{'pic_str':False},{'content':False},{'address':False},{'longitude':False},{'latitude':False}])
                    dont_param = ['content','address','longitude','latitude','pic_str']
                    for param in dont_param:
                        if param not in a_d_m: a_d_m[param] = ""
                    post_id = FCirController().release_post(a_d['uid'],a_d_m['pic_str'],a_d_m['content'],a_d_m['address'],a_d_m['longitude'],a_d_m['latitude'])
                    self.return_param(1,0,post_id,'发布成功')

            elif a_d['action'] == 'send_comment': #对说说做评论
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['post_id','comm_content'])
                    if not FCirController().judge_post_exist(a_d_m['post_id']):return self.return_param(0,200,{},options.post_not_exist)
                    comm_id = FCirController().send_comment(a_d['uid'],a_d_m['post_id'],a_d_m['comm_content'])
                    self.return_param(1,0,comm_id,'评论成功')

            elif a_d['action'] == 'update_cir_back':#更新用户朋友圈背景图
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['pic_path'])
                    UserController().update_cir_back(a_d['uid'],a_d_m['pic_path'])
                    pic_path = options.ipnet + a_d_m['pic_path']
                    self.return_param(1,0,{'pic_path':pic_path},'success')
            elif a_d['action'] == 'delete_post':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['post_id'])
                    # self.write(a_d_m)
                    if not FCirController().judge_post_exist(a_d_m['post_id']):
                        return self.return_param(0,200,{},'不存在该条互动信息')
                    post_uid = int(PostModel().get_uid(a_d_m['post_id']))
                    if not int(a_d['uid']) == post_uid:  return self.return_param(0,200,{},'您不能删除其他用户的互动消息')
                    #allowed to delete user post 
                    PostModel().delete_post(a_d_m['post_id'])
                    return self.return_param(1,0,{},'删除成功')
        except Exception,e:
            self.treat_except(e)

class PostLovePubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action'])
            if a_d['action'] == 'get_lover_list':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['page','post_id'])
                    lover_list = FCirController().get_lover_list(a_d_m['post_id'],a_d_m['page'])
                    self.return_param(1,0,lover_list,'success')
        except Exception,e:
            self.treat_except(e)

class PostLovePriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','token','version','action'])
            if not UsersModel().check_token_available(a_d['uid'],a_d['token']): return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'send_love':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['post_id'])
                    if not FCirController().judge_post_exist(a_d_m['post_id']):return self.return_param(0,200,{},options.post_not_exist)
                    result = FCirController().send_love(a_d['uid'],a_d_m['post_id'])
                    if not result: return self.return_param(0,200,{},'您已经赞过了')
                    self.return_param(1,0,{},'success')
            else:
                pass
        except Exception,e:self.treat_except(e)


class ShareHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action'])
            if a_d['action'] == 'share_post':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['post_id'])
                    if not FCirController().judge_post_exist(a_d_m['post_id']):return self.return_param(0,200,{},options.post_not_exist)
                    share_info = ShareController().share_post(a_d_m['post_id'])
                    return self.return_param(1,0,share_info,'success')
            elif a_d['action'] == 'share_note':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['note_id'])
                    if not NoteController().judge_note_exist(a_d_m['note_id']): return self.return_param(0,200,{},options.note_not_exist)
                    share_info = ShareController().share_note(a_d_m['note_id'])
                    return self.return_param(1,0,share_info,'success')
            elif a_d['action'] =='share_org_act':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['activity_id'])
                    share_info = ShareController().share_org_act(a_d_m['activity_id'])
                    return self.return_param(1,0,share_info,'success')

        except Exception,e:
            self.treat_except(e)


class FollowPubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action'])
            if a_d['action'] == 'get_follower_list':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['page'])
                    f_list = FollowController().get_follower_list(a_d['uid'],a_d_m['page'])
                    return self.return_param(1,0,f_list,'success')

            elif a_d['action'] == 'get_following_list':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['page'])
                    f_list = FollowController().get_following_list(a_d['uid'],a_d_m['page'])
                    return self.return_param(1,0,f_list,'success')
        except Exception,e:
            self.treat_except(e)

class OrgPriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action','token'])
            if not UsersModel().check_token_available(a_d['uid'],a_d['token']):
                pass
                # return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'apply_club_org':#
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['contacts','contact_phone','address','name','type','athletics',{'qq':False,'email':False}])
                    if int(a_d_m['type']) not in set([1,2]): return self.return_param(0,200,{},"类型只能为１或者２　")
                    a_d_m['user_id'] = a_d['uid']
                    a_d_m['create_time'] = PublicFunc.get_current_datetime()
                    OrganizationApplyModel().save_apply_info(a_d_m)
                    return self.return_param(1,0,{},"谢谢申请，审核中")
            elif a_d['action'] == 'set_field':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['field','new_value','id'])
                    result = OrgClubController().set_field(a_d_m['id'],a_d['uid'],a_d_m['field'],a_d_m['new_value'])
                    if not result is True: return self.return_param(0,200,{},result)
                    return self.return_param(1,0,{},'修改成功')
            elif a_d['action'] == 'get_apply_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id','page'])
                    result = OrgClubController().get_apply_list(a_d_m['id'],a_d['uid'],a_d_m['page'])#the id is organization_id 
                    if result['flag'] == 0: return self.return_param(0,200,{},result['ret'])
                    else:
                        info_return = {}
                        info_return['per_page'] = 8
                        info_return['apply_list'] = result['ret']
                    return self.return_param(1,0,info_return,'success')
            elif a_d['action'] == 'pass_apply':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['apply_id',{'oper':False}])
                    if 'oper' not in a_d_m: a_d_m['oper'] = 1 #pass the apply of the users 
                    OrgClubController().apply_oper(a_d_m['apply_id'],a_d_m['oper'])
                    return self.return_param(1,0,{},"操作成功")


            elif a_d['action'] == 'focus_org_oper':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id'])
                    result = OrgClubController().focus_org_oper(a_d['uid'],a_d_m['id'])
                    self.return_param(1,0,result,'success')
            elif a_d['action'] == 'attend_org':
                if a_d['version'] >=  options.add_org_version:
                    a_d_m = self.get_multi_argument(['id',{"excuse":False}])
                    if not 'excuse' in a_d_m: a_d_m['excuse'] = ''
                    result = OrgClubController().attend_org(a_d['uid'],a_d_m['id'],a_d_m['excuse'])
                    return self.return_param(1,0,{},result)
            elif a_d['action'] == 'release_album':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['album_id','pic_str','org_id'])
                    result = OrgClubController().release_album(a_d['uid'],a_d_m['album_id'],a_d_m['pic_str'],a_d_m['org_id'])
                    self.return_param(1,0,{},'success')
            elif a_d['action'] == 'create_album':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['org_id','album_name'])
                    result = OrgClubController().create_album(a_d['uid'],a_d_m['org_id'],a_d_m['album_name'])
                    if isinstance(result,str):
                        return self.return_param(0,200,{},result)
                    return self.return_param(1,0,{"id":result,"name":a_d_m['album_name']},'success')

        except Exception,e:
            self.treat_except(e)


class OrgPubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['version','uid','action'])
            if a_d['action'] == 'get_org_club_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['type','page'])
                    info = OrgClubController().get_org_club_list(a_d_m['type'],a_d_m['page'])
                    return self.return_param(1,0,info,'success')

            elif a_d['action'] == 'get_my_org_club':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['page'])
                    info = OrgClubController().get_my_org_club_list(a_d['uid'],a_d_m['page'])
                    return self.return_param(1,0,info,'success')
                
            elif a_d['action'] == 'search_by_id_name':
                if a_d['action'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['search','page'])
                    info = OrgClubController().search_by_id_name(a_d_m['search'],a_d_m['page'])
                    self.return_param(1,0,info,'success')
            elif a_d['action'] == 'get_brief':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id'])
                    info = OrgClubController().get_brief_info(a_d_m['id'],a_d['uid'])
                    self.return_param(1,0,info,'success')
            elif a_d['action'] == 'get_dy_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['organization_id','page'])
                    dy_list = OrgClubController().get_dy_list(a_d_m['organization_id'],a_d_m['page'])
                    return self.return_param(1,0,dy_list,'success')

            elif a_d['action'] == 'get_album_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['organization_id','page'])
                    dy_list = OrgClubController().get_album_list(a_d_m['organization_id'],a_d_m['page'])
                    return self.return_param(1,0,dy_list,'success')

            elif a_d['action'] == 'get_member_list':#获取机构成员列表
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['organization_id','page'])
                    member_list = OrgClubController().get_member_list(a_d_m['organization_id'],a_d_m['page'])
                    return self.return_param(1,0,member_list,'success')



            elif a_d['action'] == 'get_album_pic_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['org_id','album_id','last_id'])
                    if 'current_date' not in a_d_m: a_d_m['current_date'] = None 
                    pic_list = OrgClubController().get_album_pic_list(a_d_m['org_id'],a_d_m['album_id'],a_d_m['last_id'],a_d_m['current_date'])
                    self.return_param(1,0,pic_list,'success')

            elif a_d['action'] == 'judge_is_admin':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id'])#organize_id
                    result = OrgClubController().judge_is_admin(a_d['uid'],a_d_m['id'])
                    return self.return_param(1,0,result,'success')
            elif a_d['action'] == 'get_user_role':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['organ_id'])
                    role = OrgClubController().get_user_role(a_d['uid'],a_d_m['organ_id'])
                    self.return_param(1,0,{'role_id':role},'success')

            elif a_d['action'] == 'get_album_info':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['album_id'])
                    album_info = OrgClubController().get_album_info(a_d_m['album_id'])
                    return self.return_param(1,0,album_info,'success')



#                     主要是原生显示，后端的数据
# 1、一次数据，最多给出6行图片（当前是一行4张图片）
# 2、一次最多显示两天的数据，及当前所在日期，与下一套图片的日期
# 3、如果当天数据剩余>=6行，仅增加当天数据
# 4、如果当天数据剩余<6行，则还会附加下一套的剩余行数的数据
# 5、基于4，如果下一套数据>=剩余行数，则直接获得所需数据
# 6、基于4，如果下一套数据<剩余行数，则仅显示剩余行数数据，不会继续同时增加，第三套数据
# 7、如果已经没有数据了，需要提示，“已经到达相册最后”



        except Exception,e:
            raise
            self.treat_except(e)

class ActPubHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['version','uid','action'])
            if a_d['action'] == 'get_act_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id','page'])
                    act_list = ActController().get_act_list(a_d_m['id'],a_d_m['page'])
                    self.return_param(1,0,act_list,'success')
            elif a_d['action'] == 'get_agree_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id','page'])
                    agree_list = ActController().get_agree_list(a_d_m['id'],a_d_m['page'])
                    self.return_param(1,0,agree_list,'success')
            elif a_d['action'] == 'get_attend_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id','page'])#id is activity_id
                    attend_list = ActController().get_attend_list(a_d_m['id'],a_d_m['page'])
                    self.return_param(1,0,attend_list,'success')
            elif a_d['action'] == 'get_act_info':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['activity_id'])
                    act_info = ActController().get_act_info(a_d['uid'],a_d_m['activity_id'])
                    self.return_param(1,0,act_info,'success')
            elif a_d['action'] == 'get_activity_list':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['page'])
                    act_list = ActController().get_activity_list(a_d_m['page'])
                    return self.return_param(1,0,act_list,'success')



                    # 1、进行中的（活动结束时间正序），
                    # 2、报名中的（报名结束时间正序），
                    # 3、等待进行中的（已经报名结束，但还未开始，活动开始时间正序），
                    # 4、还未开始报名的（报名开始时间正序），
                    # 5、已经结束的（活动结束时间倒序）



        except Exception,e:
            self.treat_except(e)

class ActPriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','version','action','token'])
            if not UsersModel().check_token_available(a_d['uid'],a_d['token']):
                pass
                # return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'agree_act':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['id'])
                    result = ActController().agree_act(a_d_m['id'],a_d['uid'])
                    if not result is True: return self.return_param(0,200,{},result)
                    self.return_param(1,0,{},'操作成功')
            elif a_d['action'] == 'attend_act':
                if a_d['version'] >= options.add_org_version:
                    a_d_m = self.get_multi_argument(['truename','sex','tel','activity_id'])
                    # if a_d_m['sex'] not in set(['1,','2']): 
                    result = ActController().attend_act(a_d_m['activity_id'],a_d['uid'],a_d_m['truename'],a_d_m['sex'],a_d_m['tel'])
                    if not result is True: return self.return_param(0,200,{},result)
                    self.return_param(1,0,{},'success')
            elif a_d['action'] == 'get_user_info':
                if a_d['version'] >= options.add_org_version:
                    user_info = self.db.get("select username,sex,tel   from fs_users where uid = %s",a_d['uid'])
                    return self.return_param(1,0,user_info,'success')

        except Exception,e:
            self.treat_except(e)




class FollowPriHandler(BaseHandler):
    def get(self):
        try:
            a_d = self.get_multi_argument(['uid','token','version','action'])
            if not UsersModel().check_token_available(a_d['uid'],a_d['token']):
                return self.return_param(0,200,{},options.wrong_login_tip)
            if a_d['action'] == 'follow_man':#去关注其他人
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['fuid'])
                    result = FollowController().following_man(a_d['uid'],a_d_m['fuid'])
                    return self.return_param(1,0,{'result':result},'操作成功!')
            elif a_d['action'] == 'follow_other':
                if a_d['version'] >= '3.2':
                    a_d_m = self.get_multi_argument(['fuid'])
                    result = FollowController().follow_other(a_d['uid'],a_d_m['fuid'])
                    return self.return_param(1,0,{'result':result},'success')

        except Exception,e:
            self.treat_except(e)

class GroupHandler(BaseHandler):

    def get(self):
        action = self.get_argument('action')
        if action == 'get_group_info':#get the all group info 
            try:
                group_id = self.get_argument('id')
                group_info = self.groupmodel.get_group_info(group_id)
                self.return_param(1,0,group_info,'成功')#return the data
            except Exception,e:self.treat_except(e)

        elif action == 'get_detail_group_info':#get more info include group_mem and group_mem_rank and my rank 
            try:
                a_d = self.get_multi_argument(['id','uid'])
                group_info = self.groupmodel.get_group_info(a_d['id']) 
                user_info_some_return = self.groupmemmodel.get_group_user_info_list(a_d['id'],int(options.mem_num_show))
                user_info_point_some_return = self.groupmemmodel.get_group_user_point_rank(a_d['id'],int(options.mem_point_show_num))
                return_dict = {'group_info':group_info,'user_info_some_return':user_info_some_return,'user_info_point_some_return':user_info_point_some_return}
                self.return_param(1,0,return_dict,'获取成功')
            except Exception,e: self.treat_except(e)

        elif action == 'get_all_group':  #get my group list 
            try:
                uid = self.get_argument('uid')
                my_group_list = self.groupmemmodel.get_my_group_list(uid)
                leader_group_info_return = my_group_list[0]
                group_info_return = my_group_list[1] #获取我所加入的团队
                invite_list_return = self.invitemodel.get_group_invite_list(uid)
                return_dict = {'group_info_return':group_info_return,'leader_group_info_return':leader_group_info_return,'invite_list_return':invite_list_return}
                self.return_param(1,0,return_dict,'成功')
            except Exception,e: 
                raise
                self.treat_except(e)
       
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
            if 'token' in a_d and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # for that there is no  uid 
            try:
                self.groupmodel.change_group_mem_num(a_d['id'],-1)
                self.groupmemmodel.delete_group_mem(a_d['id'],a_d['uid'])
            except Exception,e: self.treat_except(e)
            self.return_param(1,0,{},'成功')

        elif action == 'break_group': #break up a group  you are  the leader of the group  finish
            a_d = self.get_multi_argument(['uid','id',{'version':False,'token':False}])
            if 'token' in a_d and a_d['version'] == options.token_request_more_version: self.usersmodel.check_token_available(a_d['uid'],a_d['token'])
            try: self.groupmodel.delete_group(a_d['id'])
            except Exception,e: self.treat_except(e)
            self.return_param(1,0,{},'成功')

        elif action == 'show_all_members':#finish
             group_id = self.get_argument('id')
             try: 
                group_user_list = self.groupmemmodel.get_group_user_info_list(group_id,-1)
                self.return_param(1,0,group_user_list,'成功')
             except Exception,e: self.treat_except(e)
             
        elif action == 'show_all_rank':#finish
            try:
                group_id = self.get_argument('id')
                user_info_point_return = self.groupmemmodel.get_group_user_point_rank(group_id)
                self.return_param(1,0,user_info_point_return,'成功')
            except Exception,e: self.treat_except(e)

        elif action == 'del_mem':
            a_d = self.get_multi_argument(['token','uid','id','del_uid','version'])#id is group_id
            try:
                if a_d['version'] == options.token_request_more_version: self.usersmodel.check_token_available(a_d['uid'],a_d['token'])
                if int(self.get_group_info(group_id,['leader_id'])['leader_id']) == int(a_d['del_uid']): 
                    return self.return_param(0,201,{},'you can not delete youself')
                if not self.groupmodel.check_is_leader(a_d['uid'],a_d['id']): return self.return_param(0,200,{},'the user is not the leader')
                self.groupmemmodel.delete_group_mem(a_d['id'],a_d['del_uid'])
                self.groupmodel.change_group_mem_num(self,a_d['id'],-1)
                self.return_param(1,0,{},'成功')
            except Exception,e: self.treat_except(e)

    def post(self):
        action = self.get_argument('action')
        if action == 'create_group':   #create a new group 
            a_d = self.get_multi_argument(['uid','group_name','group_intro','group_tag_id',{'token':False,'version':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # of if the leader of the group is that man ?? 
            group_info = {'group_name':a_d['group_name'],'intro':a_d['group_intro'],'leader_id':a_d['uid'],'tag_id':a_d['group_tag_id'],'membernum':1,'createtime':int(time.time())}
            group_id = self.insert_into_db('fs_group',group_info)
            self.insert_into_db('fs_group_mem',{'group_id':group_id,'is_leader':1,'attendtime':int(time.time()),'uid':a_d['uid']})
            self.return_param(1,0,{'id':group_id},'成功')

        elif action == 'change_param':
            a_d = self.get_multi_argument(['param','id',{'token':False,'version':False,'uid':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # of if the leader of the group is that man ?? 
            if a_d['param'] == 'groupname': 
                new_groupname = self.get_argument('new_groupname')
                self.groupmodel.change_group_info(a_d['id'],group_name=new_groupname)
                self.return_param(1,0,{},'成功')
            elif a_d['param'] == 'group_intro': #change the group intro
                new_group_intro = self.get_argument('new_group_intro')
                self.groupmodel.change_group_info(a_d['id'],intro=new_group_intro)
                self.return_param(1,0,{},'成功')
            else: pass

class InviteHandler(BaseHandler):

    def get(self):
        a_d = self.get_multi_argument(['action','id',{'version':False,'token':False,'uid':False}])
        if 'token' in a_d and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token']) # for that there is no  uid 
        if a_d['action'] == 'pass_invite':
            try:
                invite_info = self.invitemodel.get_invite_info(a_d['id'])
                if self.groupmemmodel.judge_alreay_in_group(invite_info['uid'],invite_info['group_id']): return self.return_param(0,200,{},'您已经在该团队中！') 
                self.groupmemmodel.add_mem_to_group(invite_info['uid'],invite_info['group_id']) 
                self.groupmodel.change_group_mem_num(invite_info['group_id'],1)
                group_name = self.get_group_info(invite_info['group_id'])['group_name']
                userinfo = self.usersmodel.get_import_user_info(invite_info['uid'],['username','tel'])
                self.invitemodel.delete_invite(a_d['id'])
                content = "(%s)(%s) 已经通过了你的 '%s'团队邀请" % (userinfo['username'],userinfo['tel'],group_name)
                self.send_sysinfo(invite_info['uid'],content,'好友通过邀请')
                self.return_param(1,0,{},'成功') 
            except Exception,e: self.treat_except(e)

        elif a_d['action'] == 'refuse_invite':
            try:
                self.invitemodel.delete_invite(a_d['id'])
                self.return_param(1,0,{},'成功')
            except Exception,e:self.treat_except(e)
        else: pass

    def post(self): 
        action = self.get_argument('action')
        if action == 'invite_friends':
            try:
                a_d = self.get_multi_argument(['id','tel',{'version':False,'token':False,'uid':False}])
                if 'token' in a_d and a_d['version'] == options.token_request_more_version: 
                    self.usersmodel.check_token_available(a_d['uid'],a_d['token']) 
                if not self.usersmodel.check_tel_register(a_d['tel']): return self.return_param(0,200,{},'该用户还没有注册')
                uid = self.usersmodel.get_uid_via_tel(a_d['tel'])
                if self.invitemodel.judge_alreay_send_invite(uid,a_d['id']): return self.return_param(0,201,{},'邀请已发送，等待对方同意')
                if self.groupmemmodel.judge_alreay_in_group(uid,a_d['id']):  return self.return_param(0,202,{},'该用户已经在团队内')
                if self.invitemodel.write_group_invite(uid,a_d['id']):  return self.return_param(1,0,{},'成功')
            except Exception,e:self.treat_except(e)
  
class OrgHandler(BaseHandler):  #yinshuai
    def get(self):
        action = self.get_argument('action')
        if action == 'get_org': # search the organizition
            a_d = self.get_multi_argument(['word'])
            self.return_param(1,0,self.find_some('fs_org',['username AS name'],username={'rule':'LIKE','value':'%%' + a_d['word'] + '%%'}),'success')


class NotifyHandler(BaseHandler):
    """wecha notify """
    def get(self):
        action = self.get_argument('action')
        if action == 'get_attend_info':
            attend_info = self.get_attend_info(self.get_argument('id'))
            event_info = self.get_event_info(attend_info['eid'])
            if int(attend_info['group_id']):#group_attend
                mem_num = self.find_db_sum('fs_user_event',out_trade_no=attend_info['out_trade_no'])
                self.return_param(1,0,{'ename':event_info['ename'],'epayfee':float(event_info['epayfee'])*mem_num,'out_trade_no':attend_info['out_trade_no']},'success')
            else:#person attend
                self.return_param(1,0,{'ename':event_info['ename'],'epayfee':float(event_info['epayfee']),'out_trade_no':attend_info['out_trade_no']},'success')


        elif action == 'weipay_notify':
            out_trade_no = self.get_argument('out_trade_no')
            if out_trade_no[0:1] == 'a': self.update_db('fs_user_assoc',{'checkstatus':1},{'out_trade_no':out_trade_no})
            else: 
                order_info = self.db.get("select checkstatus from fs_user_event where out_trade_no = %s limit 1 ",out_trade_no)
                if int(order_info['checkstatus']):
                    return 'success'
                self.update_db('fs_user_event',{'checkstatus':1},{'out_trade_no':out_trade_no})
                for ele in order_info:
                    eid = int(ele['eid'])
                    etel = ele['etel']
                    if eid in set([203,204,205,206]):
                        send_content = "你已成功报名2016中国·房山世界地质公园京津冀越野障碍跑挑战赛，请你仔细阅读竞赛办法，关注赛事动态，准时参与赛事。感谢你的参与"
                        PublicFunc.send_sms(etel,send_content)


        elif action == 'pay_success_send_msg':
            a_d_m = self.get_multi_argument(['out_trade_no'])
            order_info = self.db.get("select  checkstatus  from fs_user_event where out_trade_no = %s limit 1",a_d_m['out_trade_no'])
            if int(order_info['checkstatus']):
                return 'success'
            for ele in order_info:
                eid = int(ele['eid'])
                etel = ele['etel']
                etel = "18811399881"
                if eid in set([203,204,205,206]):
                    # send_content = "你已成功报名#2016中国·房山世界地质公园京津冀越野障碍跑挑战赛#，请你仔细阅读竞赛办法，关注赛事动态，准时参与赛事。感谢你的参与！"
                    send_content = "你已成功报名2016中国·房山世界地质公园京津冀越野障碍跑挑战赛，请你仔细阅读竞赛办法，关注赛事动态，准时参与赛事。感谢你的参与"
                    PublicFunc.send_sms(etel,send_content)
        elif action == 'test_msg':
            etel = "15010568383"
            send_content = "你已成功报名2016中国·房山世界地质公园京津冀越野障碍跑挑战赛，请你仔细阅读竞赛办法，关注赛事动态，准时参与赛事。感谢你的参与"
            # send_content = "您好!恭喜您成功报名8月7日(周日)上午8:30在良乡体育中心举办的青创动力2016年科学健身运动项目推广活动,请您于8月5日下午两点到良乡体育中心综合馆领取服装"
            # send_content = "您好!恭喜您成功报名8月7日(周日)上午8:30在良乡体育中心举办的青创动力2016年科学健身运动项目推广活动,请您于8月5日下午两点到良乡体育中心综合馆领取服装"
            print send_content
            print etel
            PublicFunc.send_sms(etel,send_content)


      
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

    def post(self):
        action = self.get_argument('action')
        if action == 'post_apply':
            a_d = self.get_multi_argument(['id','uid',{'version':False,'token':False}])
            if a_d.has_key('token') and a_d['version'] == options.token_request_more_version: self.check_token_available(a_d['uid'],a_d['token'])
            leader_id = self.get_group_info(a_d['id'])['leader_id']
            if self.alreay_in_group(a_d['uid'],a_d['id']): return self.return_param(0,201,{},'你已经在该团队中')
            if self.add_user_to_group(a_d['uid'],a_d['id']): return self.return_param(1,0,{},'加入成功')

class ThirdHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'wecha':
            a_d = self.get_multi_argument([{'nickname':False},{'sex':False},{'province':False},{'city':False},{'country':False},{'avatar':False},'unionid'])
            try:
                user_info = self.wechausermodel.wecha_user_get(a_d)
                if user_info[0] == 'exist':
                    uid = user_info[1]
                elif user_info[0] == 'create': 
                    uid = self.usersmodel.create_null_user()
                    self.wechausermodel.bind_user_wecha_user(user_info[1],uid)#false bind 
                token = self.usersmodel.update_user_token(uid)
                bind_layer_show = 1 if self.usersmodel.judge_show_bind_layer(uid) else 0
                self.return_param(1,0,{'uid':uid,'token':token,'bind_layer_show':bind_layer_show},'success')
            except Exception,e: 
                self.treat_except(e)    
        else: pass

class BindHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        a_d_m = self.get_multi_argument(['token','version','uid'])
        if a_d_m['version'] == options.token_request_more_version:
            if not self.usersmodel.check_token_available(a_d_m['uid'],a_d_m['token']):
                return self.return_param(0,200,{},'您已经注销登录或者在其他地方登录，请重新登录')
        if action == 'bind_tel':
            pass
        elif action == 'send_bind_code':
            try:
                tel = self.get_argument('tel')
                result = self.usersmodel.send_wecha_bind_tel_code(tel,a_d_m['uid'])
                if result is True: return self.return_param(1,0,{},'发送成功')
                else: return self.return_param(0,200,{},result)
            except Exception,e: self.treat_except(e)

        elif action == 'treat_tel_bind':#微信绑定手机号
            try:
                a_d = self.get_multi_argument(['tel','code'])
                result = self.usersmodel.treat_tel_bind(a_d['tel'],a_d['code'],a_d_m['uid'])
                if result is True: self.return_param(1,0,{},'绑定成功')
                else: self.return_param(0,200,{},result) 
            except Exception,e:self.treat_except(e)

        elif action == 'treat_bind_wecha':#手机号登录的用户 去绑定微信
            """用户现在是以手机号的方式来登录的，那么用户这次提交的uid就是手机号登录之后获取到的uid,"""
            try:
                if self.wechausermodel.judge_uid_in_wecha_user(a_d_m['uid']): return self.return_param(0,200,'{}','该手机账号已经绑定微信！')
                a_d = self.get_multi_argument(['nickname','sex','province','city','country','avatar','unionid'])
                wecha_info = self.wechausermodel.wecha_user_get(a_d) 
                if wecha_info[0] == 'create': #如果刚刚把用户的微信信息写入的话，那么直接把手机用户uid绑定到上面去
                    self.wechausermodel.bind_user_wecha_user(wecha_info[1],a_d_m['uid'])
                elif wecha_info[0] == 'exist':#如果微信用户已经存在的话
                    if self.usersmodel.get_wecha_bind_tel(wecha_info[1]): return self.return_param(0,200,{},'该微信号已经被绑定！')
                    #微信的数据最终还是皈依到手机账号上面去,就是说微信上的数据（也就是之前的没有tel的uid）的数据要混合在被绑定的手机uid上
                    self.usersmodel.delete_user_via_pk(wecha_info[1])#那么先把之前的那个没有手机号码的主表的数据软删除 wecah_info[1] 当中存储的是之前绑定的主用户表中的uid
                    self.wechausermodel.bind_user_wecha_user(wecha_info[2],a_d_m['uid']) #可以绑定了
                return self.return_param(1,0,{},'绑定成功!')
            except Exception,e: self.treat_except(e)

        elif action == 'refuse_show_bind_layer':
            try:
                if self.usersmodel.refuse_show_bind_layer(a_d_m['uid']): return self.return_param(1,0,{},'成功')
            except Exception,e: self.treat_except(e)

        elif action == 'get_bind_info':#获取各种渠道的绑定状态
            try:
                bind_info = self.usersmodel.get_bind_info(a_d_m['uid'])
                return self.return_param(1,0,bind_info,'成功')
            except Exception,e:self.treat_except(e)

class LoginHandler(BaseHandler):
    def get(self):
        a_d = self.get_multi_argument(['version','tel','password'])
        if a_d['version'] >= options.token_request_more_version:
            try:
                user_info = UserController().login(a_d['tel'],a_d['password'])
                if user_info == 0: return self.return_param(0,200,{},'用户还没有注册')
                if user_info == 1: return self.return_param(0,200,{},'密码错误')
                MUserModel().add_info_mongo(user_info[1])
                return self.return_param(1,0,{'token':user_info[0],'uid':user_info[1],'bind_layer_show':user_info[2]},'登录成功')
            except Exception,e:
                self.treat_except(e)

class LogoutHandler(BaseHandler):
    def get(self):
        a_d = self.get_multi_argument(['uid','action','token'])
        if a_d['action'] == 'logout':
            try:
                # if not self.usersmodel.check_token_available(a_d['uid'],a_d['token']):   return self.return_param(0,200,{},'系统出错了！请重试!')
                if self.usersmodel.logout(a_d['uid']):  return self.return_param(1,0,{},'注销成功!')
            except Exception,e: self.treat_except(e)

class SystemHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'get_sysinfo':
            try:
                uid = self.get_argument('uid')
                sysinfo_list = self.systemmodel.get_sysinfo(uid)
                self.return_param(1,0,sysinfo_list,'成功')
            except Exception,e: print e

        elif action == 'del_sysinfo':
            id = self.get_argument('id')
            if self.systemmodel.del_sysinfo(id): return self.return_param(1,0,{},'成功')

        elif action == 'get_ad': #get the picList of the add
            ad_list = self.admodel.get_all_ad()
            self.return_param(1,0,ad_list,'成功')

class AdminSendHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')
        if action == 'send_sms':
            result = self.usersmodel.send_admin_bind_code('18811399881')
            print result
            if result is True: return self.return_param(1,0,{},'发送成功')
            else: self.return_param(0,200,{},result)

class TagHandler(BaseHandler):
    def get(self):
        try:
           tag_all = self.tagmodel.get_all_tag()
           self.return_param(1,0,tag_all,'成功')
        except Exception,e:self.treat_except(e)
  

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
