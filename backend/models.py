from mongoengine import *


# class meta(Document):
#     meta = StringField()
#     groups = ListField()
    # favorites = ListField(StringField())

class users(Document):
    username = StringField()
    password = StringField()
    type = StringField()
    gender = StringField()
    points = StringField()
    last_login = DateTimeField()
    login_count = IntField()
    mobile = IntField()


# class Category(Document):
#     categoryID = IntField()
#     nextUpdateTime = DateTimeField()
#
#
# class Article(Document):
#     articleID = StringField()
#     categoryID = StringField()
#     author = StringField(default="Unknown")
#     title = StringField(default="N/A")
#     description = StringField(default="N/A")
#     summary = StringField(default="N/A")
#     comments = ListField(StringField())
#
#
# class Comment(Document):
#     commentID = StringField()
#     authorID = StringField()
#     articleID = StringField()
#     comment = StringField()
#     timeStamp = DateTimeField(default=datetime.now)
#
#
# class Token(Document):
#     username = EmailField()
#     token = StringField()
#     expires = DateTimeField()
