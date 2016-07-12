


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

