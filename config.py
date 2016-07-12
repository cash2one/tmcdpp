#!/usr/bin/env python
#-*- coding: UTF-8 -*
#coding:utf-8 
# -*- coding: utf-8 -*-
from tornado.options import define, options

# define("test",default="44",help="")
#open debug mode 
define("debug",default=True,help="debug mode",type=bool)

#the setting of the debug mode to print differant except sentence 
define("is_debug",default=True,help="is debug mode",type=bool)
define("port", default=8888, help="run on the given port", type=int)

####mysql config 
# define("mysql_host", default="192.168.239.1:3306", help="blog database host")
define("mysql_host", default="101.200.214.68:3306", help="blog database host")
define("mysql_database", default="fitness", help="blog database name")
define("mysql_user", default="root", help="blog database user")
define("mysql_password", default="tZ3BtYCeQLdwyKqF", help="blog database password")#the password of mysql is null

define('redis_host',default="127.0.0.1",help="redis host")
define('redis_port',default="7000",help="redis port")
define('redis_db',default="0",help="redis db")

#mongodb config  
define('mongodb_host',default="127.0.0.1",help="set the host of the mongo")
define('mongodb_port',default="27017",help="set the mongo port ")
define('mongodb_db',default="fitness",help="set the data db")

#expire times config  
define('group_info_expires',default="3600",help="group info will clear from cache after 1 hours")
define('group_user_list_expires',default="3600",help="group_user_list will clear from cache after 1 hour")
define('user_info_expires',default="36000",help="user_info will clear from cache after 10 hours")
define('mygroup_expires',default="36000",help="the group which me is not the leader expires")
define('leadergroup_expires',default="36000",help="the group which i an the leader")
define('game_info_expires',default="36000",help="the expires of the game info is 10 hours ")
define('game_lives_expires',default="18000",help="the expires of the game lives is 5 hours ")
define('game_lives_all_expires',default="18000",help="the expires of the game lives all is 5 hours ")
define('game_intro_expires',default="18000",help="the expires of the game intro")
define('game_agreement_expires',default="18000",help="the expire of the game agreement")
define('recent_run_man',default="10",help="the expires of the 6 recent run man")
define('rank_data_expires',default="10",help="the expires of the rank_data_expires")
define('group_show_num',default="20",help="")
#
define('ipnet',default="http://101.200.214.68",help="this is the ipnet of the resourse")
define('recent_show',default="6",help="show the recent run man or group num ")
define('html_path',default="/home/yinshuai/",help="set the default html file save path")
define('token_request_more_version',default="3.0",help="version 3")
define('note_circle_v',default="3.2",help="version3.2")
define('default_nick_name',default="小跑男",help="")
define('note_per_page',default="20",help="")
define('post_per_page',default="3",help="")
define('post_love_len',default="10",help="")
define('post_content_show_len',default="10",help="")
define('note_comm_per_page',default="5",help="")
define('post_comm_per_page',default="5",help="")
define('post_lover_per_page',default="15",help="")
define('wrong_login_tip',default="您还没有登录！")
define('mem_num_show',default="6",help="the num of mem show in the group page")
define('mem_point_show_num',default="5",help="the num of mem pointer show ")
define('note_save_num',default="3",help="个人信息中存储帖子") 
define('following_save_num',default="10",help="个人信息中存储到关注的人")
define('follower_save_num',default="10",help="个人信息中存储自己到粉丝")
define('following_per_page',default="10",help="")
define('group_get_num',default='2',help="")
define('follower_per_page',default="10",help="")
define('friends_find_per_page',default="10",help="")
define('group_save_num',default="3",help="团队最大保存数")
define('post_not_exist',default="不存在该条互动信息",help="")
define('note_not_exist',default="不存在该条帖子",help="")
define('post_thumb_save_path',default="/Uploads/PostPic/")


define('share_title',default="下载全民健身Ready Go,享受运动乐趣",help="")
define('bind_tel_expires',default="300",help="the expire of the bind tel")

