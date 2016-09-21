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
from Models.musermodel import MUserModel
from Models.followmodel import FollowModel
from Models.organizationinfomodel import OrganizationInfoModel
from Models.organizationapplymodel import OrganizationApplyModel
from Models.organizationusermodel import OrganizationUserModel
from Models.organizationstatusmessagemodel import OrganizationStatusMessageModel
from Models.organizationalbummodel import OrganizationAlbumModel
from Models.photomodel import PhotoModel
from Func.publicfunc import PublicFunc

TYPE_NEW_MEMBER = 1 
TYPE_MEMBER_ATTEND =2 
TYPE_NOT_MEMBER_ATTEND = 3 
TYPE_NEW_ACT_STORE = 11 
TYPE_ACT_START = 11 
TYPE_ACT_END = 13
PIC_PER_ROW = 4 
PIC_ROW_MAX = 6 
DATE_MAX =2 



class OrgClubController:
	def __init__(self):
		pass

	def get_org_club_list(self,type,page):
		info = OrganizationInfoModel().get_org_club_list(type,page)
		for ele in info:
			ele['create_time'] = ele['create_time'][:10]
			ele['img_path'] = options.ipnet + ele['img_path']
			ele['logo_path'] = options.ipnet + ele['logo_path']
			ele['athletics'] = ele['athletics'].split("|")[:3]
			star = self.get_star(ele['score'])
			ele['star_pic'] = self.get_star_pic(ele['score'])
		return info 

	def get_my_org_club_list(self,uid,page):
		info = OrganizationUserModel().get_my_org_club_list(uid,page)
		list_return =[]
		for org_ele in info:
			org_id = org_ele['organization_id']
			org_info = OrganizationInfoModel().get_brief_info(org_id)
			org_info['create_time'] = org_info['create_time'][:10]
			org_info['img_path'] = options.ipnet + org_info['img_path']
			org_info['logo_path'] = options.ipnet + org_info['logo_path']
			org_info['athletics'] = org_info['athletics'].split("|")[:3]
			org_info['star_pic'] = self.get_star_pic(org_info['score']) 
			list_return.append(org_info)
		return list_return 

# create_album(a_d['uid'],a_d_m['org_id'],a_d_m['album_name'])

	def create_album(self,uid,org_id,album_name):
		is_admin = OrganizationUserModel().judge_is_admin(org_id,uid)
		if not is_admin: return "只有管理员可以更改机构/俱乐部信息"
		result = OrganizationAlbumModel().create_album(uid,org_id,album_name)
		return result


	def get_album_info(self,album_id):
		info = OrganizationAlbumModel().get_album_info(album_id)
		return info

	def get_star(self,score):
		"""
		根据积分获取星级(共5级)
		"""
		scores = int(score)
		scores_list = [0,1000,3000,8000,20000]
		scores_list.append(int(score))
		scores_list.sort()
		return scores_list.index(score)

	def get_star_pic(self,score):
		star = self.get_star(score)
		return options.ipnet + '/staticPic/stars/' + str(star) + '.png' 


	def get_user_role(self,uid,organ_id):
		role = OrganizationUserModel().get_user_role(uid,organ_id)
		return role



		# get_brief_info(a_d_m['id'])
	def get_brief_info(self,id,uid):
		"""
		获取机构/俱乐部详细信息
		"""
		info = OrganizationInfoModel().get_brief_info(id)
		info['create_time'] = info['create_time'][:9]
		info['img_path'] = options.ipnet  + info['img_path']
		info['notice'] = info['notice'].split("||")
		info['athletics'] = info['athletics'].split('|')[:3]
		info['stars'] = self.get_star_pic(info['score'])
		info['need_check'] = 1 
		###check if the user has attend the club 
		role = OrganizationUserModel().judge_user_role(id,uid)
		info['can_attend'] = 0 
		info['status_name'] = ""
		if role is 0 or role is 1:#如果用户角色是管理员或者普通成员，则显示已经加入
			info['can_attend'] = 0 
			info['status_name'] = "已经加入"
		elif role is 2 or role is False :
			info['can_attend'] = 1
			info['status_name'] = "加入机构"

		####get the focus status 
		info['has_focus'] = 1 if  OrganizationUserModel().judge_has_focus(id,uid) else 0 
		return info 

	def get_member_list(self,organization_id,page):
		print 'the page is ' + str(page)
		member_list = OrganizationUserModel().get_member_list(organization_id,page)
		for mem_info in member_list:
			user_id =  mem_info['user_id']
			mem_info['role'] = 1 if mem_info['type'] & 4  else 0 #如果用户是管理员则role为1 如果为0表示是普通成员
			user_info = UsersModel().get_import_user_info(user_id,['avatar','nickname'])
			mem_info['avatar'] = user_info['avatar']
			mem_info['nickname'] = options.default_nick_name if not  user_info['nickname'] else user_info['nickname']
			del mem_info['type']

		return member_list


	def search_by_id_name(self,search,page):
		"""
		"""
		info = OrganizationInfoModel().search_by_id_name(search,page)
		for ele in info:
			ele['create_time'] = ele['create_time'][:10]
			ele['logo_path'] = options.ipnet + ele['logo_path']
			ele['athletics'] = ele['athletics'].split("|")[:3]
			star = self.get_star(ele['score'])
			ele['star_pic'] = self.get_star_pic(ele['score'])
		return info


	def set_field(self,id,uid,field,new_value):
		is_admin = OrganizationUserModel().judge_is_admin(id,uid)
		if not is_admin: return "只有管理员可以更改机构/俱乐部信息"
		if field == 'join_type' and int(new_value) not in set([0,1]):
			 return "join_type应该是0或者1"
		OrganizationInfoModel().set_field(id,field,new_value)
		return True

	def judge_is_admin(self,uid,organization_id):
		"""
		"""
		is_admin = OrganizationUserModel().judge_is_admin(organization_id,uid)
		return 1 if is_admin else 0


		# release_album(a_d['uid'],a_d_m['album_id'],a_d_m['pic_str'])

	def release_album(self,uid,album_id,pic_str,org_id):
		"""
		"""
		pic_list = []
		pic_num = len(pic_str.split(','))
		OrganizationAlbumModel().incr_photo_num(album_id,pic_num)
		for pic in pic_str.split(','):
			file_name = pic[-17:]
			PhotoModel().add_pic(uid,album_id,file_name,org_id)
		return 

	def get_apply_list(self,id,uid,page):
		is_admin = OrganizationUserModel().judge_is_admin(id,uid)
		if not is_admin: return {"flag":0,'ret':"只有管理员可以更改机构/俱乐部信息"}
		apply_list_return = OrganizationUserModel().get_apply_list(id,page)
		for ele in apply_list_return:
			uid = ele['user_id']
			user_info = UsersModel().get_import_user_info(uid,['avatar','nickname'])
			ele['nickname']  =  user_info['nickname']  if user_info['nickname'] else options.default_nick_name
			ele['avatar'] = user_info['avatar']
			ele['change_date'] = ele['change_date'][:16]
		return {'flag':1,'ret':apply_list_return}

	def apply_oper(self,apply_id,oper):
		"""
		#get the apply info 
		when the oper is 1 means pass the user request 
		when the oper is 0 means ignore the user request 
		"""
		if not int(oper):
			OrganizationUserModel().ignore_apply(apply_id)
		else:
			OrganizationUserModel().pass_apply(apply_id)
		return True

	def get_dy_list(self,organization_id,page):
		"""
		获取动态列表，根据不同的type有不同的显示范式  type为1表示这种谁谁加入，谁谁报名活动了
		type为2表示发布了什么活动等
		"""
		dy_list = OrganizationStatusMessageModel().get_dy_list(organization_id,page)
		for dy in dy_list:
			dy['target_img'] = options.ipnet + dy['target_img']
			dy['target_img'] = options.ipnet + '/Uploads/pic1.jpg'
			stamp = PublicFunc.date_to_stamp(dy['create_time'])
			dy['create_time'] = PublicFunc.time_format_span(stamp,int(time.time()))
		return_info = {}
		return_info['per_page'] = options.dy_per_page
		return_info['dy_list'] = dy_list
		return return_info

	def get_album_list(self,organization_id,page):
		"""
		仅仅获取相册和封面  
		"""
		return_list = {}
		return_list['per_page'] = 5 ##
		album_list =  OrganizationAlbumModel().get_album_list(organization_id,page)
		for album in album_list:
			album['pic'] = options.ipnet + '/Uploads/back.jpg'
		return_list['album_list'] = album_list
		return return_list

	def get_album_pic_list(self,organization_id,album_id,last_id,current_date):
		"""
		获取相册图片列表
		input param:
			last_stamp: 最后一张图片的时间戳
			current_date 当前相册日期

			PIC_PER_ROW = 4 
			PIC_ROW_MAX = 6 
			DATE_MAX =2 
		"""

		OrganizationAlbumModel().incr_album_click(album_id)
		max_get = PIC_PER_ROW * PIC_ROW_MAX# 24 
		if not int(last_id):#if the value of the latest_id is 0 ,then it request the data at the first time 
			last_id = 0 #如果是从第最开始取的话
		#if not fetch 24 pic means 
		pic_list = PhotoModel().get_album_pic_list(organization_id,album_id,last_id,max_get)
		if len(pic_list) == 0: return []
		info_return = []
		date_pic_list = {}
		date_pic_list_2 = {}
		first_pic_stamp = pic_list[0]['create_time']
		first_date = PublicFunc.stamp_to_Ymd(first_pic_stamp)
		first_date_stamp = PublicFunc.date_to_stamp(first_date + " 00:00:00")
		calc_once = 0#只计算一次新日期  
		next_date = ''# init the next_date
		lenth_of_current_date = 0 #当前date的数据量。 
		pic_max_next_date = 24 #init the max rows of the nextdate data 
		pic_max_num_next_date = 0#
		for pic_info in pic_list:
			if  pic_info['create_time'] > first_date_stamp:#如果照片是第一批的照片
				date_pic_list['date'] = first_date
				date_pic_list.setdefault('pic_list',[])
				pic_info['pic_path'] = options.ipnet + '/Uploads/AlbumPic/' + pic_info['file_name']
				pic_info['pic_thumb_path'] = options.ipnet + '/Uploads/AlbumPic/' + 't' + pic_info['file_name']
				del pic_info['file_name']
				date_pic_list['pic_list'].append(pic_info) 
				lenth_of_current_date += 1 ####auto add 1
				if len(date_pic_list['pic_list']) == max_get: break;
			else:#这个是更早日期的
				#计算新的日期, 通过新的一行数据
				if not calc_once:
					new_date_late_stamp = pic_info['create_time']
					next_date = PublicFunc.stamp_to_Ymd(new_date_late_stamp)
					calc_once += 1  
					pic_num_left = 24 - lenth_of_current_date
					if pic_num_left < 4:break
					pic_max_next_date = pic_num_left - pic_num_left%4
				date_pic_list_2['date'] = next_date
				date_pic_list_2.setdefault('pic_list',[])
				if len(date_pic_list_2['pic_list']) < pic_max_next_date:
					pic_info['pic_path'] = options.ipnet + '/Uploads/AlbumPic/' + pic_info['file_name']
					pic_info['pic_thumb_path'] = options.ipnet + '/Uploads/AlbumPic/' + 't' + pic_info['file_name']
					del pic_info['file_name']
					date_pic_list_2['pic_list'].append(pic_info)
				else:break
		info_return.append(date_pic_list)
		if date_pic_list_2:info_return.append(date_pic_list_2)
		return info_return

	def focus_org_oper(self,user_id,organization_id):
		focus_status = OrganizationUserModel().judge_has_focus(organization_id,user_id)
		if not focus_status:#if not has focus 
		 	OrganizationUserModel().add_focus(organization_id,user_id)
			return "已关注"
		else:
			OrganizationUserModel().cancel_focus(organization_id,user_id)
			return "关注"


	def attend_org(self,uid,id,excuse):
		need_check =OrganizationInfoModel().judge_need_check(id)
		is_member = OrganizationUserModel().judge_is_member(id,uid)
		if is_member: return "您已经在该机构中"
		OrganizationUserModel().set_user_member(id,uid,excuse)
		return "加入成功" if not int(need_check) else "审核中"










		
