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

from mongoengine import *


app = Flask(__name__)
CORS(app)  # 跨域访问

# models
class users(Document):
    username = StringField(required=True)
    password = StringField(required=True)
    type = StringField(required=True)
    gender = StringField(required=True)
    points = StringField(required=True)
    last_login = DateTimeField(required=True,default=datetime.datetime.now())
    login_count = IntField(required=True,default=0)
    mobile = IntField(required=True)
    def __str__(self):
        return self.username


#----- meta ------
class groups(EmbeddedDocument):
    groupname=StringField(required=True)
    index=IntField(required=True)

class topics(EmbeddedDocument):
    topicname=StringField(required=True)
    index=IntField(required=True)

class metas(Document):
    name = StringField(required=True)
    id_count = IntField(required=True)
    groups = ListField(EmbeddedDocumentField(groups),required=True)
    topics = ListField(EmbeddedDocumentField(topics),required=True)
#----- meta end------

class tasks(Document):
    status=IntField(required=True)
    finishtime=StringField(required=True)
    remark=StringField(required=True)
    group=StringField(required=True)
    upvoters=ListField(StringField())
    title=StringField(required=True)
    publisher=StringField(required=True)
    base_score=IntField(required=True)
    participators=ListField(StringField())
    tasker_other=ListField(StringField())
    tasker_main=StringField(required=True)
    ddl=IntField(required=True)
    # id=IntField(required=True)
    urgency=StringField(required=True)

# 登录及用户认证
# client = MongoClient('120.27.123.112', 27017)
# client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
# uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
# client = MongoClient(uri)

connect('sparkbition', host='120.27.123.112', username='fqs1', password='123456')

salt = '5aWZak2n35Wk fqsws'
tasks_modify = ['publisher', 'remark', 'group', 'upvoters', 'title', 'participators', 'tasker_other', 'tasker_main','ddl', 'urgency']


user=users.objects.first()
print user


def sendsms(publisher, title, person, mobile,tpl_id):
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username="任意"
        user=users.objects(username=username).first()
        if user:
            g.username=username
            user.last_login=datetime.datetime.now()
            return f(*args, **kwargs)
        resp = make_response('wrong cookies', 401)
        return resp
    return decorated_function

def changestatus(task_id,status):
    task=tasks.objects(id=task_id).first()
    user=tasks.objects(username=g.username).first()
    if (user.type == 'admin') or (user.type == 'root') or (g.username == task.tasker_main.encode('utf-8')):
        timestamp = int(time.time() * 1000)
        task.status=status
        task.finishtime=timestamp
        task.save()
        return (True,timestamp)
    else:
        return (False,'not allowed')


@app.route('/sparkbition/api/task')
@login_required
def task():
    groupinfo=metas.objects(name='groupinfo').first()
    result = []
    for group in groupinfo.groups:
        obj_tasks=tasks.objects(group=group.groupname,status__gte=0,status__lte=2)
        ret_tasks=[]
        for task in obj_tasks:
            ret_tasks.append(dict(task.to_mongo()))
        print ret_tasks
        group=dict(group.to_mongo())
        group['tasks']=ret_tasks
        result.append(group)
    resp = make_response(dumps(result), 200)
    return resp

@app.route('/sparkbition/api/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    user=users.objects(username=username).first()
    if (user == None):
        resp = make_response('wrong username')
        return resp
    if hashlib.md5(password + salt).hexdigest() == user.password:
        resp = make_response('success', 200)
        if user.login_count=='':
            user.login_count=1
        else:
            user.login_count=user.login_count+1
        user.last_login=datetime.datetime.now()
        user.save()
        resp.set_cookie('All_Hail_Fqs', base64.b64encode(salt + username.encode('utf-8')),max_age=100000)
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
    user_name = g.username
    user=users.objects(username=user_name).exclude('password').first().to_mongo()
    user['last_login']= user['last_login'].isoformat()
    resp = make_response(dumps(user), 200)
    return resp

@app.route('/sparkbition/api/new_task', methods=['POST'])
@login_required
def new_task():
    user_name = g.username

    meta = metas.objects(name='groupinfo').first()
    meta.id_count+=1
    meta.save()

    text = request.json
    text.update({'id': sum, 'status': 0, 'finishtime': '', 'publisher': user_name, 'base_score': 0, 'upvoters': []})
    timestamp = int(text['ddl'])
    text['ddl'] = timestamp
    del text['id']
    v_new_task=tasks.from_json(json.dumps(text))
    v_new_task.save()
    resp = make_response('success', 200)
    tasker = text['tasker_main']
    mobile=users.objects(username=tasker).first()['mobile']
    print sendsms(user_name, text['title'].encode('utf-8'), tasker.encode('utf-8'),mobile,13216)
    for tasker in text['tasker_other']:
        print sendsms(user_name, text['title'].encode('utf-8'), tasker.encode('utf-8'),mobile,13216)
    for tasker in text['participators']:
        print sendsms(user_name, text['title'].encode('utf-8'), tasker.encode('utf-8'),mobile,13216)
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
    user_name = g.username

    tasks

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
    print sendsms(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'],13214)
    tasker = task['tasker_main']
    print sendsms(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'],13214)
    for tasker in task['tasker_other']:
        print sendsms(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'],13214)
    for tasker in task['participators']:
        print sendsms(task['title'].encode('utf-8'), '已经被删除', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'],13214)
    return resp

@app.route('/sparkbition/api/crew_list')
@login_required

def crew_list():
    usernam = g.username

    db = client['sparkbition']
    coll_users = db['users']
    username = []
    for userinfo in coll_users.find({}):
        username.append(userinfo['username'])
    aaa = dumps(username)
    resp = make_response(aaa, 200)
    return resp

@app.route('/sparkbition/api/group_list')
@login_required
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
    usernam = g.username

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
    usernam = g.username

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
    print sendsms(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    tasker = task['tasker_main']
    print sendsms(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'), tasker.encode('utf-8'),
                   coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['tasker_other']:
        print sendsms(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    for tasker in task['participators']:
        print sendsms(task['title'].encode('utf-8'), '已经被修改', task['tasker_main'].encode('utf-8'),
                       tasker.encode('utf-8'), coll_users.find_one({'username': tasker})['mobile'])
    return resp

@app.route('/sparkbition/api/archive_task')
@login_required
def archive_task():
    usernam = g.username

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
    usernam = g.username

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
    usernam = g.username

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
    usernam = g.username

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
    usernam = g.username
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


if __name__ == '__main__':
    app.debug = True
    app.run()
    # app.run(host='0.0.0.0', port= 5001)