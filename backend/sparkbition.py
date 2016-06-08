# coding:utf-8

from functools import wraps
from flask import Flask, request, make_response,g
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
import copy
from bson import Binary, Code
from bson.json_util import dumps, loads
from flask.ext.cors import CORS  # 跨域访问

app = Flask(__name__)
app.debug=True
CORS(app)  # 跨域访问

# 登录及用户认证
client = MongoClient('120.27.123.112', 27017)
client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
client = MongoClient(uri)

salt = '5aWZak2n35Wk fqsws'
tasks_modify = ['publisher', 'remark', 'group', 'upvoters', 'title', 'participators', 'tasker_other', 'tasker_main',
                'ddl', 'urgency']


def sendsms1(publisher, title, person, mobile):
    d = {'#publisher#': publisher, '#title#': title}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode(
        {'mobile': mobile, 'tpl_id': 13216, 'tpl_value': tpl_value, 'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s' % getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信的发送结果：%s\n' %(person, result['reason'].encode('utf-8'))
    return finalstr

def sendsms2(title, tasker_main, person, mobile):
    d = {'#title#': title, '#tasker_main#': tasker_main}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode(
        {'mobile': mobile, 'tpl_id': 13215, 'tpl_value': tpl_value, 'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s' % getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信的发送结果：%s\n' % (person, result['reason'].encode('utf-8'))
    return finalstr

def sendsms3(title, how, tasker_main, person, mobile):
    d = {'#title#': title, '#how#': how, '#tasker_main#': tasker_main}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode(
        {'mobile': mobile, 'tpl_id': 13214, 'tpl_value': tpl_value, 'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s' % getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信的发送结果：%s\n' % (person, result['reason'].encode('utf-8'))
    return finalstr


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        flag = False
        username = request.cookies.get('All_Hail_Fqs')
        if (username == None) or (username == ''):
            resp = make_response('no login', 401)
            return resp
        usernam = base64.b64decode(username)
        usernam = usernam[18:]

        for user in client['sparkbition']['users'].find():
            if (user['username'].encode('utf-8') == usernam):
                g.usernam=usernam

                db = client['sparkbition']
                coll_users = db['users']
                coll_users.update({'username': usernam}, {'$set': {'last_login': datetime.datetime.now()}})
                return f(*args, **kwargs)
        if (not flag):
            resp = make_response('wrong cookies', 401)
            return resp
    return decorated_function

def changestatus(task_id,status):
    db = client['sparkbition']
    coll_tasks = db['tasks']
    tasker_main = coll_tasks.find_one({'id': int(task_id)})['tasker_main']
    coll_users = db['users']
    usertype = coll_users.find_one({'username': g.usernam})['type']
    if (usertype == 'admin') or (usertype == 'root') or (g.usernam == tasker_main.encode('utf-8')):
        timestamp = int(time.time() * 1000)
        coll_tasks.update({'id': int(task_id)}, {'$set': {'status': status, 'finishtime': timestamp}})
        return (True,timestamp)
    else:
        return (False,'not allowed')

@app.route('/sparkbition/api/checklogin')

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
@login_required
def task():
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
        if usernam['login_count']=='':
            login_count=1
        else:
            login_count=usernam['login_count']+1
        coll_users.update({'username': username},{'$set':{'login_count':login_count,'last_login': datetime.datetime.now()}})
        resp.set_cookie('All_Hail_Fqs', base64.b64encode(salt + username.encode('utf-8')))
    else:
        resp = make_response('wrong password', 200)
    return resp

@app.route('/sparkbition/api/logout')
@login_required
def logout():
    resp = make_response('success', 200)
    resp.set_cookie('All_Hail_Fqs', '')
    return resp

@app.route('/sparkbition/api/userinfo')
@login_required
def userinfo():
    usernam = g.usernam
    db = client['sparkbition']
    coll = db['users']
    a1 = coll.find_one({'username': usernam})
    del a1['password']
    a1['last_login'] = a1['last_login'].isoformat()
    aaa = dumps(a1)
    resp = make_response(aaa, 200)
    return resp

# @app.route('/sparkbition/api/func1')
# def func1():
#     username = request.cookies.get('All_Hail_Fqs')
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
@login_required
def new_task():
    usernam = g.usernam

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
    print sendsms1(usernam, text['title'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    for tasker in text['tasker_other']:
        print sendsms1(usernam, text['title'].encode('utf-8'), tasker.encode('utf-8'),
                       coll_users.find_one({'username': tasker})['mobile'])
    for tasker in text['participators']:
        print sendsms1(usernam, text['title'].encode('utf-8'), tasker.encode('utf-8'),
                       coll_users.find_one({'username': tasker})['mobile'])
    return resp


@app.route('/sparkbition/api/complete_task')
@login_required
def complete_task():
    task_id = request.args.get('task_id')
    result = changestatus(task_id,1)
    if result[0]:
        resp = make_response(json.dumps({'timestamp': result[1]}),200)
    else:
        resp = make_response(result[1],403)
    return resp

    # coll_users = db['users']
    # for tasker in coll_users.find():
    #     print sendsms2(coll_tasks.find_one({'id': int(task_id)})['title'].encode('utf-8'), coll_tasks.find_one({'id': int(task_id)})['tasker_main'].encode('utf-8'), tasker['username'].encode('utf-8'), tasker['mobile'])


@app.route('/sparkbition/api/redo_task')
@login_required
def redo_task():
    task_id = request.args.get('task_id')
    result = changestatus(task_id, 0)
    if result[0]:
        resp = make_response(json.dumps({'timestamp': 0}), 200)
    else:
        resp = make_response(result[1], 403)
    return resp


@app.route('/sparkbition/api/delete_task')
@login_required
def delete_task():
    usernam = g.usernam

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
    print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    tasker = task['tasker_main']
    print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['tasker_other']:
        print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['participators']:
        print sendsms3(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    return resp

@app.route('/sparkbition/api/crew_list')
@login_required

def crew_list():
    usernam = g.usernam

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
    db = client['sparkbition']
    coll_meta = db['meta']
    groupname = []
    for groupinfo in coll_meta.find_one({'meta': 'groupinfo'})['groups']:
        groupname.append(groupinfo['groupname'])
    aaa = dumps(groupname)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/upvote')
@login_required
def upvote():
    usernam = g.usernam

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
@login_required
def modify_task():
    usernam = g.usernam

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
        if(modify['ddl']):modify['ddl'] = int(modify['ddl'])
        coll_tasks.update({'id': text['id']}, {'$set': modify})
        resp = make_response('success', 200)
    else:
        resp = make_response('not allowed', 200)
        return resp

    task = coll_tasks.find_one({'id': text['id']})
    tasker = task['publisher']
    print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    tasker = task['tasker_main']
    print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['tasker_other']:
        print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['participators']:
        print sendsms3(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    return resp

@app.route('/sparkbition/api/archive_task')
@login_required
def archive_task():
    usernam = g.usernam

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
@login_required
def mytask():
    usernam = g.usernam

    db = client['sparkbition']
    coll_tasks = db['tasks']
    my = [{'groupname': '我发布的', 'index': 0}, {'groupname': '我负责的', 'index': 1}, {'groupname': '我参与的', 'index': 2}]
    tasks = []
    for task in coll_tasks.find({'publisher': usernam, 'status': {'$gte': 0, '$lte': 2}}):
        tasks.append(task)
    my[0].update({'tasks': tasks})
    tasks = []
    for task in coll_tasks.find({'$or': [{'tasker_other': {'$in': [usernam]}}, {'tasker_main': usernam}],
                                 'status': {'$gte': 0, '$lte': 2}}):
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
@login_required
def set_base_score():
    usernam = g.usernam

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
@login_required
def change_password():
    usernam = g.usernam

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
    resp.set_cookie('All_Hail_Fqs', '')
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

def personal_score(usernam):

    db = client['sparkbition']
    coll_tasks = db['tasks']
    score = {'all': 0, 'month': 0, 'week': 0,'chart':{'labels':["六", "五", "四", "三", "二", "一", "零"],'data':[[0,0,0,0,0,0,0]]}}

    now = time.localtime()
    this_week = time.time() - ((now.tm_wday * 24 + now.tm_hour) * 60 + now.tm_min) * 60 - now.tm_sec
    this_month = time.time() - (((now.tm_mday-1) * 24 + now.tm_hour) * 60 + now.tm_min) * 60 - now.tm_sec

    for task in coll_tasks.find({'$or': [{'tasker_other': {'$in': [usernam]}}, {'tasker_main': usernam}],'status': {'$gt': 0}}):
        this_score = float(task['base_score'])*(1 + len(task['upvoters']) * 0.1)
        if (task['tasker_main']!=usernam):
            this_score/=2
        score['all'] += this_score
        if (task['finishtime']):
            finish_time = int(task['finishtime'])/1000
            if (finish_time >= this_week):
                score['week'] += this_score
            weekTh = int((this_week - finish_time) / (3600 * 24 * 7) + 1)
            if (weekTh < 7):
                score['chart']['data'][0][6 - weekTh] += this_score

            if (finish_time >= this_month):
                score['month'] += this_score
    return score

def personal_average(score,number):
    average = copy.deepcopy(score)
    if (number['all']>0):
        average['all']/=number['all']
    if (number['week']>0):
        average['week']/=number['week']
    if (number['month']>0):
        average['month']/=number['month']
    for i in [0,6]:
        if (number['chart']['data'][0][i] > 0):
            average['chart']['data'][0][i] /= number['chart']['data'][0][i]
    return average

def personal_number(usernam):
    db = client['sparkbition']
    coll_tasks = db['tasks']
    number = {'all': 0, 'month': 0, 'week': 0, 'chart':{'labels':["六", "五", "四", "三", "二", "一", "零"],'data':[[0,0,0,0,0,0,0]]}}

    now = time.localtime()
    this_week = time.time() - ((now.tm_wday * 24 + now.tm_hour) * 60 + now.tm_min) * 60 - now.tm_sec
    this_month = time.time() - (((now.tm_mday - 1) * 24 + now.tm_hour) * 60 + now.tm_min) * 60 - now.tm_sec

    for task in coll_tasks.find({'$or': [{'tasker_other': {'$in': [usernam]}}, {'tasker_main': usernam}],'status': {'$gt': 0}}):
        number['all'] += 1
        if (task['finishtime']):
            finish_time = int(task['finishtime']) / 1000
            if (finish_time >= this_week):
                number['week'] += 1

            weekTh=int((this_week-finish_time)/(3600*24*7)+1)
            if(weekTh<7):
                number['chart']['data'][0][6-weekTh] += 1

            if (finish_time >= this_month):
                number['month'] += 1

    return number

@app.route('/sparkbition/api/statistic/personal')
@login_required
def dumps_personal():
    usernam = g.usernam
    ret={}
    ret['score']=personal_score(usernam)
    ret['number']=personal_number(usernam)
    ret['average']=personal_average(ret['score'],ret['number'])

    return dumps(ret)


# rank

def number_rank():
    db = client['sparkbition']
    coll_tasks = db['tasks']
    number={}
    for task in coll_tasks.find({'status': {'$gt': 0}}):
        task['tasker_other'].append(task['tasker_main'])
        for member in task['tasker_other']:
            if(not number.has_key(member)):
                number[member]=0
            number[member] += 1
    return number

def score_rank():
    db = client['sparkbition']
    coll_tasks = db['tasks']
    score={}
    for task in coll_tasks.find({'status': {'$gt': 0}}):
        task['tasker_other'].append(task['tasker_main'])
        for member in task['tasker_other']:
            if(not score.has_key(member)):
                score[member]=0
            this_score = float(task['base_score']) * (1 + len(task['upvoters']) * 0.1)
            if (task['tasker_main'] != member):
                this_score /= 2
            score[member] += this_score
    return score

def ave_rank(score,number):
    ave=copy.deepcopy(score)
    for k,v in ave.iteritems():
        ave[k]=v/number[k]
    return ave

@app.route('/sparkbition/api/statistic/ranking')
@login_required
def dumps_rank():
    ret = {}
    score = score_rank()
    number = number_rank()
    average = ave_rank(score,number)
    score=sorted(score.iteritems(),key=lambda d:d[1],reverse=True)
    number=sorted(number.iteritems(),key=lambda d:d[1],reverse=True)
    average=sorted(average.iteritems(),key=lambda d:d[1],reverse=True)

    ret['number']= [{'rank':number.index(x)+1,'name': x[0],'value': x[1]} for x in number]
    ret['average']= [{'rank':average.index(x)+1,'name': x[0],'value': x[1]} for x in average]
    ret['score']= [{'rank':score.index(x)+1,'name': x[0],'value': x[1]} for x in score]
    return dumps(ret)


@app.route('/sparkbition/api/bbs_thread', methods=['GET'])
@login_required
def show_all_card():
    db = client['sparkbition']
    coll_card = db['card']
    ret = []
    for card in coll_card.find({}):
        del card['replies']
        ret.append(card)
    return dumps(ret)

@app.route('/sparkbition/api/bbs_thread/<id>', methods=['GET'])
@login_required
def show_card(id):
    db = client['sparkbition']
    coll_card = db['card']
    card=coll_card.find_one({'id': id})
    return dumps(card)

@app.route('/sparkbition/api/bbs_thread', methods=['POST'])
@login_required
def create_card():
    usernam = g.usernam

    db = client['sparkbition']
    coll_meta = db['meta']
    id_count=coll_meta.find_one({'meta':"card"})["id_count"]
    id_count+=1

    coll_meta.update({'meta':'card'},{"$set":{"id_count":id_count}})
    coll_card = db['card']

    text = request.json
    text['id'] = str(id_count)
    text['replies']=[]
    text['author'] = usernam
    text['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    coll_tags = db['tags']
    for tag in text['tags']:
        tagexsist=coll_tags.find_one({'name':tag})
        if(not tagexsist):
            coll_tags.insert({"name":tag})
    coll_card.insert(text)

    resp = make_response('success', 200)
    return resp

@app.route('/sparkbition/api/bbs_reply',methods=['POST'])
@login_required
def bbs_reply():
    usernam = g.usernam

    db = client['sparkbition']
    coll_card = db['card']
    id=request.args.get('id')

    text = request.json
    replies=coll_card.find_one({'id':id})['replies']
    replies.append({'id': len(replies) + 1, 'author': usernam, 'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), 'content': text['content'], 'upvoters': [], 'downvoters': []})
    coll_card.update({'id': id}, {'$set': {'replies': replies}})
    return 'success'

@app.route('/sparkbition/api/bbs_tags')
def bbs_tags():
    db = client['sparkbition']
    coll_tags = db['tags']
    tags=coll_tags.find({})
    ret=[]
    for tag in tags:
        ret.append(tag['name'])
    return dumps(ret)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port= 5001)