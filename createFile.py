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

init_time = int(time.time())
print init_time
def createTime():
	random_time = random.randint(0,100)
	init_time += random_time
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(init_time)) 



def createUrl():
	return random.choice(url_list)

# 设备号		用户手机号	小区（基站）	通信时间			访问的网站
# 0000000000	0054775807	00000168		2015-04-26 02:55:46	www.baidu.com
# 0000000000	0054775807	00000168		2015-04-26 03:15:27	www.baidu.com
##############打电话在发短信之后，一定要有时间顺序
# dataline = 



tel = createTel()
jz = createJz()
url = createUrl()
print url
print tel
print jz
da = createTime()
print da

sys.exit(0)




fr = open("net.txt",'a')
fr.write('heheda\n')
fr.write('caonimei')
fr.close()