import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_apscheduler import APScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

from .exchange import OpenExchangeRatesClient

app = Flask(__name__)

Bootstrap(app)

app.config.from_pyfile('config.py')
db = MongoEngine(app)
mail = Mail(app)

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

# scheduler
dbhost = app.config['MONGODB_SETTINGS']['host']
dbname = app.config['MONGODB_SETTINGS']['db']
app.config['SCHEDULER_JOBSTORES'] = {
    'default': MongoDBJobStore(host=dbhost, database=dbname, collection='jobs')
}

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# scheduler.add_job(id='11', func=myfunc, trigger='interval', seconds=10)
