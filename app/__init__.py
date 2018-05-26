from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)

app.config.from_pyfile('config.py')
db = MongoEngine(app)
mail = Mail(app)

app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager(app)

from app.home import home as home_blueprint
app.register_blueprint(home_blueprint)

from app.user import user as user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/user')

login_manager.login_view = "home.login"