from datetime import datetime
from enum import IntEnum
from bson.objectid import ObjectId

from flask_login import UserMixin

from app import db
import app.constants as constants
import app.utils as utils


# incomes
# expenses


class MoneyEntry(db.EmbeddedDocument):
    class Recurring(IntEnum):
        SINGLE = 0
        EVERY_DAY = 1
        EVERY_MONTH = 2
        EVERY_YEAR = 3

    class Type(IntEnum):
        INCOME = 0
        EXPENSE = 1

    id = db.ObjectIdField(required=True, default=ObjectId,
                          unique=True, primary_key=True)
    type = db.IntField(required=True, default=Type.INCOME)
    description = db.StringField(required=True)
    value = db.FloatField(required=True, default=1.00)
    currency = db.StringField(required=True, default=constants.DEFAULT_CURRENCY)
    category = db.StringField(required=True)
    date = db.DateTimeField(default=datetime.now)
    recurring = db.IntField(default=Recurring.SINGLE)

    def is_recurring(self) -> bool:
        return self.recurring != MoneyEntry.Recurring.SINGLE

    def clone(self):
        entry = MoneyEntry()
        entry.type = self.type
        entry.description = self.description
        entry.value = self.value
        entry.currency = self.currency
        entry.category = self.category
        entry.date = self.date
        entry.recurring = self.recurring
        return entry


class Settings(db.EmbeddedDocument):
    currency = db.StringField(default=constants.DEFAULT_CURRENCY)
    locale = db.StringField(default=constants.DEFAULT_LOCALE)
    start_date = db.DateTimeField(required=True, default=utils.year_month_min_date(datetime.today()))
    end_date = db.DateTimeField(required=True, default=utils.year_month_max_date(datetime.today()))


class User(UserMixin, db.Document):
    class Status(IntEnum):
        NO_ACTIVE = 0
        ACTIVE = 1
        BANNED = 2

    meta = {'collection': 'users', 'auto_create_index': False}
    email = db.StringField(max_length=30, required=True)
    password = db.StringField(required=True)
    created_date = db.DateTimeField(default=datetime.now)
    status = db.IntField(default=Status.NO_ACTIVE)

    entries = db.ListField(db.EmbeddedDocumentField(MoneyEntry), default=list)

    incomes_categories = db.ListField(db.StringField(), default=constants.INCOMES_CATEGORIES)
    expenses_categories = db.ListField(db.StringField(), default=constants.EXPENSES_CATEGORIES)

    settings = db.EmbeddedDocumentField(Settings, default=Settings)
