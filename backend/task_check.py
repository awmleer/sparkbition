# coding:utf-8

from flask import Flask, request, make_response
import time
import hashlib
import base64
import pymongo
import json
import datetime
import urllib
from pymongo import MongoClient
import bson
from bson import Binary, Code
from bson.json_util import dumps, loads
from flask.ext.cors import CORS      #跨域访问

app = Flask(__name__)
CORS(app)   #跨域访问
def sendmessage_delay(flag)
    d['#title#']=tasks.title
    if (flag==1):
        d['#how']='已经延期'
    elif flag==2:
        d['#how']='今天是DDL'
    elif flag==3:
        d['#how']='大后天是DDL'
    d['#tasker_main"']=tasks.tasker_main
    tpl_value=urllib.urlencode(d)
    getdata=urllib.urlencode({'mobile':users['mobile'],'tpl_id':flag,'tpl_value':tpl_value,'key':psb_config.smskey})
    url='http://v.juhe.cn/sms/send?%s'%getdata'
    request=urllib.urlopen(url)
    result=json.loads(request.read())
    finalstr+= '发送给%s的短信的发送结果：%s\n' %(user['username'],result['reason'])
#登录及用户认证
client = MongoClient('120.27.123.112', 27017)
client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
client = MongoClient(uri)
db=client.sparkbition
tasks_file=db['tasks']
meta_file=db['meta']
users_file=db['users']
tasks_undone=tasks_file.find({'status':'0'})
finalstr=''
for tasks in tasks_undone
    for tasker in tasks.tasker_other
        users=users_file.find('username':tasker)
        if tasks.ddl-time.time()<0:
            sendmessage(1)
        elif tasks.ddl-time.time()<86400000
            sendmessage(2)
        elif 172800000<tasks.ddl-time.time() and tasks.ddl-time.time()<259200000
            sendmessage(3)