# coding:utf-8
import time
import urllib
import json
from pymongo import MongoClient

def sendsms3(title, how, tasker_main, person, mobile):
    d = {'#title#': title, '#how#': how, '#tasker_main#': tasker_main}
    tpl_value = urllib.urlencode(d)
    finalstr = ''
    getdata = urllib.urlencode(
        {'mobile': mobile, 'tpl_id': 13214, 'tpl_value': tpl_value, 'key': 'b32c625ffb38e4ad07f86bb1101548e1'})
    url = 'http://v.juhe.cn/sms/send?%s' % getdata
    req = urllib.urlopen(url)
    result = json.loads(req.read())
    finalstr += '发送给%s的短信结果如下：%s\n' % (person, result['reason'].encode('utf-8'))
    return finalstr

#连接数据库
client = MongoClient('120.27.123.112', 27017)
client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
client = MongoClient(uri)
db=client.sparkbition
tasks_file=db['tasks']
users_db = db['users']
while True:
    for i in tasks_file.find({'status':1}):
        if 1000*time.time()-i['finishtime']>604800000:
            tasks_file.update({'id':i['id']},{'$set':{'status':2}})
            task_score = int(i['base_score']) * (1 + 0.1 * len(i['upvoters']))
            sendsms3(i['title'],"已经被关闭，您的最终得分是：".encode('utf-8') + str(task_score).encode('utf-8'),i['tasker_main'].encode('utf-8'),i['tasker_main'].encode('utf-8'),users_db.find_one({'username': i['tasker_main']})['mobile']) #主负责人
            for tasker in i['task_other']:
                sendsms3(i['title'], "已经被关闭，您的最终得分是：".encode('utf-8') + str(task_score * 0.5).encode('utf-8'), i['tasker_main'].encode('utf-8'), tasker.encode('utf-8'), users_db.find_one({'username': tasker})['mobile'])  #其他负责人
    time.sleep(1200)