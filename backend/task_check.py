#!/usr/bin/python
# coding:utf-8

import time
import urllib
from pymongo import MongoClient

def sendmessage(flag,users):
    d={}
    d['#title#']=tasks['title'].encode('utf-8')
    if (flag==1):
        d['#how#']='已经延期'
    elif flag==2:
        d['#how#']='今天是DDL'
    elif flag==3:
        d['#how#']='大后天是DDL'
    elif flag == 4:
        d["#how#"] = '一周后是DDL'
    d['#tasker_main#']=tasks['tasker_main'].encode('utf-8')
    tpl_value=urllib.urlencode(d)
    getdata=urllib.urlencode({'mobile':users['mobile'],'tpl_id':13214,'tpl_value':tpl_value,'key':'b32c625ffb38e4ad07f86bb1101548e1'})
    url='http://v.juhe.cn/sms/send?%s'%getdata
    request=urllib.urlopen(url)
    # result=json.loads(request.read())
    # finalstr+= '发送给%s的短信的发送结果：%s\n' %(user['username'],result['reason'])

def processtasker(tasker):
    users = users_file.find_one({'username': tasker})
    if tasks['ddl'] - time_now < 0:
        sendmessage(1,users)
    elif tasks['ddl'] - time_now < 86400000:
        sendmessage(2,users)
    elif 172800000 < tasks['ddl'] - time_now and tasks['ddl'] - time_now < 259200000:
        sendmessage(3,users)
    elif 518400000 < tasks['ddl'] - time_now and tasks['ddl'] - time_now < 604800000:
        sendmessage(3, users)

#登录及用户认证
client = MongoClient('120.27.123.112', 27017)
client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
client = MongoClient(uri)
db=client.sparkbition
tasks_file=db['tasks']
meta_file=db['meta']
users_file=db['users']
finalstr=''
time_now=time.time()*1000
for tasks in tasks_file.find({'status':0}):
    print "\n==============================================================\n执行到了这个任务："
    print tasks
    for tasker in tasks['tasker_other']:
        processtasker(tasker)
    for tasker in tasks['participators']:
        processtasker(tasker)
    processtasker(tasks['tasker_main'])
# print finalstr
