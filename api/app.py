from flask import Flask, g
from flask_cors import CORS 
from flask_login import LoginManager
import os 

from db import DATABASE, initialize 
from user import User
from post import Post 
from comment import Comment

from resources.users import user
from resources.posts import post
from resources.comments import comment

DEBUG = True
PORT = 8000

login_manager = LoginManager()

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET') or 'iwanttohaveapompskyoranaussieoragoldendoodlesomeday'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    try:
        return User.get(User.id == userid)
    except:
        return None

@app.before_request
def before_request():
    g.db = DATABASE 
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def index():
    return 'Welcome to Paws!'

app.register_blueprint(user)
app.register_blueprint(post)
app.register_blueprint(comment)

origins=['http://localhost:3000']

if 'DATABASE_URL' in os.environ:
    initialize([User, Post, Comment])
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    origins.append(os.environ.get('CLIENT_URL'))

CORS(app, origins=origins, supports_credentials=True)

if __name__ == '__main__':
    initialize([User, Post, Comment])
    app.run(debug=DEBUG, port=PORT)

# hi