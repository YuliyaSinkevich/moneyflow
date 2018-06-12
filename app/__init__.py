import atexit

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler

from .exchange import OpenExchangeRatesClient

app = Flask(__name__)
app.config.from_pyfile('config.py')

bootstrap = Bootstrap(app)
db = MongoEngine(app)
mail = Mail(app)

exchange = OpenExchangeRatesClient(app.config['OPEN_EXCHANGE_RATES_DB_PATH'], app.config['OPEN_EXCHANGE_RATES_APP_ID'])

# scheduler
db_host = app.config['MONGODB_SETTINGS']['host']
db_name = app.config['MONGODB_SETTINGS']['db']

job_stores = {
    'default': {'type': 'mongodb',
                'database': db_name,
                'collection': 'jobs',
                'host': db_host}
}

scheduler = BackgroundScheduler()
scheduler.configure(jobstores=job_stores)
scheduler.start()

login_manager = LoginManager(app)

# blueprint
from app.home import home as home_blueprint

app.register_blueprint(home_blueprint)

from app.user import user as user_blueprint

app.register_blueprint(user_blueprint, url_prefix='/user')

login_manager.login_view = "home.login"


# routes
@atexit.register
def on_exit():
    print('on_exit')
    scheduler.shutdown()
