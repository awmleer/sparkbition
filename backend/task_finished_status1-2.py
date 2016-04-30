# coding:utf-8
from flask import Flask, request, make_response
import time
import hashlib
import base64
import pymongo
import json
import datetime
from pymongo import MongoClient
import bson
from bson import Binary, Code
from bson.json_util import dumps, loads
from flask.ext.cors import CORS      #跨域访问

app = Flask(__name__)
CORS(app)   #跨域访问

#登录及用户认证
client = MongoClient('120.27.123.112', 27017)
client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
client = MongoClient(uri)
db=client.sparkbition
while True:
    tasks_file=db['tasks']
    status_1=tasks_file.find({'status':'1'})
    for i in status_1:
        if time.time()-i['ddl']>259200:
            i['status']=2
    time.sleep(1200)