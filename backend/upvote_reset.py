# coding:utf-8
from pymongo import MongoClient

#登录及用户认证
client = MongoClient('120.27.123.112', 27017)
client.admin.authenticate('fqs', '123456', mechanism='MONGODB-CR')
uri = "mongodb://fqs:123456@120.27.123.112/admin?authMechanism=MONGODB-CR"
client = MongoClient(uri)
db=client.sparkbition
coll_users = db['users']
coll_users.update({'_id': {'$exists': True}}, {'$set':{'upvotetimes': 5}}, multi = True)