# coding:utf-8

from flask import Flask, request, make_response
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


# db = client['sparkbition']
# coll = db['meta']
# a1 = coll.find_one({'meta': 'groupinfo'})
# temp = []
# for ii in a1['groups']:
#     temp.append(ii)
#
# coll = db['tasks']
# fuck = []
# for ii in temp:
#     ii.update({'tasks':[coll.find_one({'group': ii['groupname']})]})
#     fuck.append(ii)
# print dumps(fuck)

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
    return aaa


# @app.route('/api/login')
# def login():
#     resp = make_response('success',200)
#     resp.set_cookie('username', 'the username')
#     return resp
#
# @app.route('/api/func1')
# def func1():
#     username = request.cookies.get('username')
#     resp = make_response('failed',200)
#     if username == 'the username':
#         resp = make_response('success',200)
#     return resp
#
# @app.route('/new')
# def new():
#    username = request.args.get('username')
#    password = request.args.get('password')
#    return 'new %s %s ' %(username,password)
#
@app.route('/list/group1')
def list_group1():
   return 'Hello World!'
#
# @app.route('/hello/<person>')
# def hello(person):
#    return 'Hello %s !' % person

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port= 5001)