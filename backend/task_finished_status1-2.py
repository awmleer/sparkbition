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
    for i in tasks_file.find({'status':1}):
        if 1000*time.time()-i['finishtime']>259200000:
            tasks_file.update({'id':i['id']},{'$set':{'status':2}})
    time.sleep(1200)