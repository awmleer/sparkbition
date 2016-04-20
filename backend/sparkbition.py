# coding:utf-8

from flask import Flask, request, make_response
import time
import hashlib
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


db = client['sparkbition']
coll = db['users']
aa = '789456'
bb = hashlib.md5(aa)
abc = {'password': '213'}
coll.insert_one(abc)

@app.route('/sparkbition/api/task')
def task():
    db = client['sparkbition']
    coll = db['meta']
    a1 = coll.find_one({'meta': 'groupinfo'})
    temp = []
    for ii in a1['groups']:
        temp.append(ii)

    coll = db['tasks']
    fuck = []
    for ii in temp:
        ii.update({'tasks':[coll.find_one({'group': ii['groupname']})]})
        fuck.append(ii)
    aaa = dumps(fuck)
    resp = make_response(aaa, 200)
    return resp

@app.route('/api/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    db = client['sparkbition']
    coll = db['users']
    # cc = time.time()
    a1 = coll.find_one({'username': username})
    a2 = a1['password']
    if a2 == password:
        resp = make_response('success', 200)
        resp.set_cookie('username', username)
    else:
        resp = make_response('failed', 401)
    return resp

@app.route('/api/logout')
def logout():
    resp = make_response('success', 200)
    resp.set_cookie('username', None)
    return resp

@app.route('/api/func1')
def func1():
    username = request.cookies.get('username')
    if username != None :
        resp = make_response('success', 200)
    else:
        resp = make_response('failed', 401)
    return resp

# @app.route('/new')
# def new():
#    username = request.args.get('username')
#    password = request.args.get('password')
#    return 'new %s %s ' %(username,password)

# @app.route('/list/group1')
# def list_group1():
#    return 'Hello World!'
#
# @app.route('/hello/<person>')
# def hello(person):
#    return 'Hello %s !' % person

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port= 5001)