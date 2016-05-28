# coding:utf-8
import time
from pymongo import MongoClient

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