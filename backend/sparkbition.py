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

salt = '5aWZak2n35Wk fqsws'

# db = client['sparkbition']
# coll = db['users']
# aa = '6546'
# bb = hashlib.md5(aa + salt)
# abc = {'password': bb.hexdigest()}
# coll.insert_one(abc)

# bb = base64.b64encode(salt + aa)
# db = client['sparkbition']
# coll = db['tasks']
# abc = coll.find({'group': '主要任务'})
# aaa = []
# for i in abc:
#     aaa.append(i)
# print aaa

@app.route('/sparkbition/api/task')
def task():
    db = client['sparkbition']
    coll_meta = db['meta']
    groupinfo = coll_meta.find_one({'meta': 'groupinfo'})

    coll_tasks = db['tasks']
    result = []
    for group in groupinfo['groups']:
        temp = coll_tasks.find({'group': group['groupname'], 'status': {'$gte': 0, '$lte': 1}})
        tasks = []
        for i in temp:
            tasks.append(i)
        group.update({'tasks': tasks})
        result.append(group)
    aaa = dumps(result)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/login')
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
        resp.set_cookie('All_Hell_Fqs', base64.b64encode(salt + username))
    else:
        resp = make_response('wrong password', 200)
    return resp

@app.route('/sparkbition/api/logout')
def logout():
    resp = make_response('success', 200)
    resp.set_cookie('All_Hell_Fqs', '')
    return resp

@app.route('/sparkbition/api/userinfo')
def userinfo():
    username = request.cookies.get('All_Hell_Fqs')
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    db = client['sparkbition']
    coll = db['users']
    a1 = coll.find_one({'username': usernam})
    del a1['password']
    aaa = dumps(a1)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/func1')
def func1():
    username = request.cookies.get('All_Hell_Fqs')
    usernam = base64.b64decode(username)
    usernam = usernam[18:]

    if (username == None) or (username == ''):
        resp = make_response('failed', 401)
    else:
        resp = make_response('success', 200)

    return resp

@app.route('/sparkbition/api/new_task', methods=['POST'])             #todo 添加发送短信的功能
def new_task():
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]

    db = client['sparkbition']
    coll_meta = db['meta']
    groupinfo = coll_meta.find_one({'meta': 'groupinfo'})
    sum = groupinfo['id_count']
    sum = sum + 1
    coll_meta.update({'meta': 'groupinfo'}, {'$set': {'id_count': sum}})

    text = request.json
    coll_tasks = db['tasks']
    text.update({'id': sum, 'status': 0, 'finishtime': '', 'publisher': usernam})
    coll_tasks.insert(text)

    resp = make_response('success', 200)
    return resp

@app.route('/sparkbition/api/complete_task')                #todo 添加发送短信的功能
def complete_task():
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]

    task_id = request.args.get('task_id')
    db = client['sparkbition']
    coll_tasks = db['tasks']
    timestamp = int(time.time() * 1000)
    coll_tasks.update({'id': int(task_id)}, {'$set': {'status': 1, 'finishtime': timestamp}})
    resp = make_response(json.dumps({'finishtime': timestamp}), 200)
    return resp

@app.route('/sparkbition/api/delete_task')                  #todo 添加发送短信的功能
def delete_task():
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]

    db = client['sparkbition']
    coll_tasks = db['tasks']
    task_id = request.args.get('task_id')
    publisher = coll_tasks.find_one({'id': int(task_id)})['publisher']
    coll_users = db['users']
    usertype = coll_users.find_one({'username': usernam})['type']
    print usertype
    if (usertype == 'admin') or (usertype == 'root') or (usernam == publisher):
        coll_tasks.update({'id': int(task_id)}, {'$set': {'status': -1}})
        resp = make_response('success', 200)
    else:
        resp = make_response('not allowed', 200)
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