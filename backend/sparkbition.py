# coding:utf-8

from flask import Flask, request, make_response
import time
import urllib
import urllib2
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
tasks_modify = ['publisher', 'remark', 'group', 'upvoters', 'title', 'participators', 'tasker_other', 'tasker_main', 'ddl', 'urgency']

def sendsms1(publisher, title, person, mobile):
    d = {'#publisher#': publisher, '#title#': title}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode({'mobile':mobile,'tpl_id':13216,'tpl_value':tpl_value,'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s'%getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信的发送结果：%s\n' %(person, result['reason'].encode('utf-8'))
    return finalstr

def sendsms2(title, tasker_main, person, mobile):
    d = {'#title#': title, '#tasker_main#': tasker_main}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode({'mobile':mobile,'tpl_id':13215,'tpl_value':tpl_value,'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s'%getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信的发送结果：%s\n' %(person, result['reason'].encode('utf-8'))
    return finalstr

def sendsms3(title, how, tasker_main, person, mobile):
    d = {'#title#': title, '#how#': how, '#tasker_main#': tasker_main}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode({'mobile':mobile,'tpl_id':13214,'tpl_value':tpl_value,'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s'%getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信的发送结果：%s\n' %(person, result['reason'].encode('utf-8'))
    return finalstr

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
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_meta = db['meta']
    groupinfo = coll_meta.find_one({'meta': 'groupinfo'})

    coll_tasks = db['tasks']
    result = []
    for group in groupinfo['groups']:
        temp = coll_tasks.find({'group': group['groupname'], 'status': {'$gte': 0, '$lte': 2}})
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
    coll_users = db['users']
    usernam = coll_users.find_one({'username': username})
    if (usernam == None):
        resp = make_response('wrong username')
        return resp
    passwo = usernam['password']
    password_hash = hashlib.md5(password + salt).hexdigest()
    if passwo == password_hash:
        resp = make_response('success', 200)
        resp.set_cookie('All_Hell_Fqs', base64.b64encode(salt + username.encode('utf-8')))
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
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll = db['users']
    a1 = coll.find_one({'username': usernam})
    del a1['password']
    aaa = dumps(a1)
    resp = make_response(aaa, 200)
    return resp

# @app.route('/sparkbition/api/func1')
# def func1():
#     username = request.cookies.get('All_Hell_Fqs')
#     usernam = base64.b64decode(username)
#     usernam = usernam[18:]
#
#     if (username == None) or (username == ''):
#         resp = make_response('failed', 401)
#     else:
#         resp = make_response('success', 200)
#
#     return resp

@app.route('/sparkbition/api/new_task', methods=['POST'])
def new_task():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_meta = db['meta']
    groupinfo = coll_meta.find_one({'meta': 'groupinfo'})
    sum = groupinfo['id_count']
    sum = sum + 1
    coll_meta.update({'meta': 'groupinfo'}, {'$set': {'id_count': sum}})

    text = request.json
    coll_tasks = db['tasks']
    text.update({'id': sum, 'status': 0, 'finishtime': '', 'publisher': usernam, 'base_score': 0, 'upvoters': []})
    timestamp = int(text['ddl'])
    text['ddl'] = timestamp
    coll_tasks.insert(text)
    resp = make_response('success', 200)

    coll_users = db['users']
    tasker = text['tasker_main']
    print sendsms1(usernam, text['title'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in text['tasker_other']:
        print sendsms1(usernam, text['title'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in text['participators']:
        print sendsms1(usernam, text['title'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    return resp

@app.route('/sparkbition/api/complete_task')
def complete_task():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    task_id = request.args.get('task_id')
    db = client['sparkbition']
    coll_tasks = db['tasks']
    tasker_main = coll_tasks.find_one({'id': int(task_id)})['tasker_main']
    coll_users = db['users']
    usertype = coll_users.find_one({'username': usernam})['type']
    if (usertype == 'admin') or (usertype == 'root') or (usernam == tasker_main.encode('utf-8')):
        timestamp = int(time.time() * 1000)
        coll_tasks.update({'id': int(task_id)}, {'$set': {'status': 1, 'finishtime': timestamp}})
        resp = make_response(json.dumps({'finishtime': timestamp}), 200)
    else:
        resp = make_response('not allowed', 200)
        return resp

    # coll_users = db['users']
    # for tasker in coll_users.find():
    #     print sendsms2(coll_tasks.find_one({'id': int(task_id)})['title'].encode('utf-8'), coll_tasks.find_one({'id': int(task_id)})['tasker_main'].encode('utf-8'), tasker['username'].encode('utf-8'), tasker['mobile'])
    return resp

@app.route('/sparkbition/api/delete_task')
def delete_task():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_tasks = db['tasks']
    task_id = request.args.get('task_id')
    publisher = coll_tasks.find_one({'id': int(task_id)})['publisher']
    coll_users = db['users']
    usertype = coll_users.find_one({'username': usernam})['type']
    if (usertype == 'admin') or (usertype == 'root') or (usernam == publisher.encode('utf-8')):
        coll_tasks.update({'id': int(task_id)}, {'$set': {'status': -1}})
        resp = make_response('success', 200)
    else:
        resp = make_response('not allowed', 200)
        return resp

    task = coll_tasks.find_one({'id': int(task_id)})
    tasker = task['publisher']
    print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    tasker = task['tasker_main']
    print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['tasker_other']:
        print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['participators']:
        print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    return resp

@app.route('/sparkbition/api/crew_list')
def crew_list():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_users = db['users']
    username = []
    for userinfo in coll_users.find({}):
        username.append(userinfo['username'])
    aaa = dumps(username)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/group_list')
def group_list():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_meta = db['meta']
    groupname = []
    for groupinfo in coll_meta.find_one({'meta': 'groupinfo'})['groups']:
        groupname.append(groupinfo['groupname'])
    aaa = dumps(groupname)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/upvote')
def upvote():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_tasks = db['tasks']
    task_id = request.args.get('task_id')
    if (coll_tasks.find_one({'id': int(task_id)})['status'] != 1):
        resp = make_response('not allowed', 200)
        return resp
    upvoters = coll_tasks.find_one({'id': int(task_id)})['upvoters']
    for upvoter in upvoters:
        if (upvoter.encode('utf-8') == usernam):
            resp = make_response('already', 200)
            return resp
    upvoters.append(usernam)
    coll_tasks.update({'id': int(task_id), 'status': 1}, {'$set': {'upvoters': upvoters}})
    resp = make_response('success', 200)
    return resp

@app.route('/sparkbition/api/modify_task', methods=['POST'])
def modify_task():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_tasks = db['tasks']
    coll_users = db['users']
    text = request.json
    modify = {}
    for modify_one in tasks_modify:
        modify.update({modify_one: text[modify_one]})
    publisher = coll_tasks.find_one({'id': text['id']})['publisher']
    usertype = coll_users.find_one({'username': usernam})['type']
    if (usertype == 'admin') or (usertype == 'root') or (usernam == publisher.encode('utf-8')):
        coll_tasks.update({'id': text['id']}, {'$set': modify})
        resp = make_response('success', 200)
    else:
        resp = make_response('not allowed', 200)
        return resp

    task = coll_tasks.find_one({'id': text['id']})
    tasker = task['publisher']
    print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    tasker = task['tasker_main']
    print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['tasker_other']:
        print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['participators']:
        print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    return resp

@app.route('/sparkbition/api/archive_task')
def archive_task():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    task_id = request.args.get('task_id')
    db = client['sparkbition']
    coll_tasks = db['tasks']
    if (coll_tasks.find_one({'id': int(task_id)})['status'] != 2):
        resp = make_response('not allowed', 200)
        return resp
    publisher = coll_tasks.find_one({'id': int(task_id)})['publisher']
    coll_users = db['users']
    usertype = coll_users.find_one({'username': usernam})['type']
    if (usertype == 'admin') or (usertype == 'root') or (usernam == publisher.encode('utf-8')):
        coll_tasks.update({'id': int(task_id)}, {'$set': {'status': 3}})
        resp = make_response('success', 200)
    else:
        resp = make_response('not allowed', 200)
    return resp

@app.route('/sparkbition/api/mytask')
def mytask():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    db = client['sparkbition']
    coll_tasks = db['tasks']
    my = [{'groupname': '我发布的', 'index': 0},{'groupname': '我负责的', 'index': 1}, {'groupname': '我参与的', 'index': 2}]
    tasks = []
    for task in coll_tasks.find({'publisher': usernam, 'status': {'$gte': 0, '$lte': 2}}):
        tasks.append(task)
    my[0].update({'tasks': tasks})
    tasks = []
    for task in coll_tasks.find({'$or': [{'tasker_other': {'$in': [usernam]}}, {'tasker_main': usernam}], 'status': {'$gte': 0, '$lte': 2}}):
        tasks.append(task)
    my[1].update({'tasks': tasks})
    tasks = []
    for task in coll_tasks.find({'participators': {'$in': [usernam]}, 'status': {'$gte': 0, '$lte': 2}}):
        tasks.append(task)
    my[2].update({'tasks': tasks})
    aaa = dumps(my)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/set_base_score')
def set_base_score():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    task_id = request.args.get('task_id')
    base_score = request.args.get('base_score')
    db = client['sparkbition']
    coll_tasks = db['tasks']
    coll_users = db['users']
    usertype = coll_users.find_one({'username': usernam})['type']
    status = coll_tasks.find_one({'id': int(task_id)})['status']
    if ((status != 0) and (status != 1)):
        resp = make_response('not allowed', 200)
        return resp
    if ((usertype == 'admin') or (usertype == 'root')):
        coll_tasks.update({'id': int(task_id)}, {'$set': {'base_score': base_score}})
        resp = make_response('success', 200)
    else:
        resp = make_response('not allowed', 200)
    return resp

@app.route('/sparkbition/api/change_password')
def change_password():
    flag = False
    username = request.cookies.get('All_Hell_Fqs')
    if (username == None) or (username == ''):
        resp = make_response('no login', 401)
        return resp
    usernam = base64.b64decode(username)
    usernam = usernam[18:]
    for user in client['sparkbition']['users'].find():
        if (user['username'].encode('utf-8') == usernam):
            flag = True
            break
    if (not flag):
        resp = make_response('wrong cookies', 401)
        return resp

    old_password = request.args.get('old_password')
    new_password = request.args.get('new_password')
    db = client['sparkbition']
    coll_users = db['users']
    old_password_hash = hashlib.md5(old_password + salt).hexdigest()
    new_password_hash = hashlib.md5(new_password + salt).hexdigest()
    if (old_password_hash != coll_users.find_one({'username': usernam})['password']):
        resp = make_response('wrong old password', 200)
        return resp
    coll_users.update({'username': usernam}, {'$set': {'password': new_password_hash}})
    resp = make_response('success', 200)
    resp.set_cookie('All_Hell_Fqs', '')
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