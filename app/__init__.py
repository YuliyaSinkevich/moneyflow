from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
import os
from app.exchange import OpenExchangeRatesClient

from flask_bootstrap import Bootstrap

from flask_nav import Nav
from flask_nav.elements import *

app = Flask(__name__)

Bootstrap(app)

app.config.from_pyfile('config.py')
db = MongoEngine(app)
mail = Mail(app)
nav = Nav(app)

exchange_client = OpenExchangeRatesClient(app.config['OPEN_EXCHANGE_RATES_DB_PATH'],
                                          app.config['OPEN_EXCHANGE_RATES_APP_ID'])

app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager(app)

from app.home import home as home_blueprint

app.register_blueprint(home_blueprint)

from app.user import user as user_blueprint

app.register_blueprint(user_blueprint, url_prefix='/user')

login_manager.login_view = "home.login"

app.config['BOOTSTRAP_SERVE_LOCAL'] = True


@nav.navigation()
def index():
    config = app.config['PUBLIC_CONFIG']
    return Navbar(config['site']['title'], View('Home', 'home.start'), )
