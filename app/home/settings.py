from datetime import datetime

from app import db
import app.utils as utils
import app.constants as constants


class Settings(db.EmbeddedDocument):
    currency = db.StringField(default=constants.DEFAULT_CURRENCY)
    locale = db.StringField(default=constants.DEFAULT_LOCALE)
    start_date = db.DateTimeField(required=True, default=utils.year_month_min_date(datetime.today()))
    end_date = db.DateTimeField(required=True, default=utils.year_month_max_date(datetime.today()))
