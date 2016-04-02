from flask import Flask
from flask import request
from flask.ext.cors import CORS    #跨域请求

app = Flask(__name__)
CORS(app)


@app.route('/api/login')
def login():
    resp = make_response(render_template(...))
    resp.set_cookie('username', 'the username')
    return resp




#@app.route('/new')
#def new():
 #   username = request.args.get('username')
  #  password = request.args.get('password')
   # return 'new %s %s ' %(username,password)

#@app.route('/list/group1')
#def list_group1():
 #   return 'Hello World!'

#@app.route('/hello/<person>')
#def hello(person):
 #   return 'Hello %s !' % person

if __name__ == '__main__':
    app.run(host='0.0.0.0')