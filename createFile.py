#coding=utf-8
import sys
import random
import time

url_list  = ['www.baidu.com','www.sina.com','www.iqiyi.com','www.2233.com','www.a.com','www.b.com','www.c.com','www.d.com','www.e.com',
			   'www.mi.com','www.shit.com','www.lenove.com','www.huawei.com','www.ping.com','bbs.byr.cn','tv.byr.cn','bt.byr.cn']

def createTel():
	tel_head = '188113998'
	tel_tail_first = random.randint(6,9)			   
	tel_tail_second = random.randint(0,9)
	tel = tel_head + str(tel_tail_first) + str(tel_tail_second)
	return tel

def createJz():
	jz_head = '00000'
	jz_first = random.randint(8,9)
	jz_second = random.randint(0,9)
	jz = jz_head + str(jz_first) + str(jz_second)
	return jz

	
# def createTime():
# 	random_time = random.randint(0,100)
# 	init_time += random_time
 
def stamp_to_date(stamp):
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(stamp))


def createUrl():
	return random.choice(url_list)

# 设备号		用户手机号	小区（基站）	通信时间			访问的网站
# 0000000000	0054775807	00000168		2015-04-26 02:55:46	www.baidu.com
# 0000000000	0054775807	00000168		2015-04-26 03:15:27	www.baidu.com
##############打电话在发短信之后，一定要有时间顺序
# dataline = 


# 位置数据  duanxin  haishi 通话通信 还是其他通信 卡机   基站 通信时间 
# 			小区（基站）   基站         通信时间
# 0000000000	0054775807	2  00000054		2015-04-26 04:20:27

sb_num = '0000000000'

fr_net = open("net.txt",'a')#open the file
fr_tel = open("tel.txt",'a')
init_time = int(time.time())
for _ in range(100000):	
	tel = createTel()
	jz = createJz()
	url = createUrl()
	time_incr = random.randint(0,3600)
	init_time += time_incr
	date_net = stamp_to_date(init_time)
	net_line = sb_num + '\t' + tel + '\t' + jz + '\t' + date_net + '\t' + url + '\n'
	init_time += time_incr
	date_tel = stamp_to_date(init_time)
	tel_type = random.randint(0,3)
	tel_line = sb_num + '\t' + tel + '\t' + str(tel_type) + '\t' + jz + '\t' + date_tel + '\n'
	fr_net.write(net_line)
	fr_tel.write(tel_line)
 
fr_net.close()