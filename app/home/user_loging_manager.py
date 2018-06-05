from flask_login import UserMixin
from app import db
from datetime import datetime
from enum import IntEnum
from bson.objectid import ObjectId
import app.constants as constants
import app.utils as utils


# incomes
# expenses


class MoneyEntry(db.EmbeddedDocument):
    id = db.ObjectIdField(required=True, default=ObjectId,
                          unique=True, primary_key=True)
    description = db.StringField(required=True)
    value = db.FloatField(required=True)
    currency = db.StringField(required=True)
    category = db.StringField(required=True)
    date = db.DateTimeField(default=datetime.now)


class Language(db.EmbeddedDocument):
    language = db.StringField(default=constants.DEFAULT_LANGUAGE.language())
    locale = db.StringField(default=constants.DEFAULT_LANGUAGE.locale())

    def to_language(self) -> constants.Language:
        return constants.Language(self.language, self.locale)


class DateRange(db.EmbeddedDocument):
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=True)


def new_date_range():
    start_date, end_date = utils.year_month_date(datetime.today())
    return DateRange(start_date, end_date)


class Settings(db.EmbeddedDocument):
    currency = db.StringField(default=constants.DEFAULT_CURRENCY)
    language = db.EmbeddedDocumentField(Language, default=Language)
    date_range = db.EmbeddedDocumentField(DateRange, default=new_date_range())


class User(UserMixin, db.Document):
    class Status(IntEnum):
        NO_ACTIVE = 1
        ACTIVE = 2
        BANNED = 3

    meta = {'collection': 'users'}
    email = db.StringField(max_length=30, required=True)
    password = db.StringField(required=True)
    created_date = db.DateTimeField(default=datetime.now)
    status = db.IntField(default=Status.NO_ACTIVE)

    incomes = db.ListField(db.EmbeddedDocumentField(MoneyEntry), default=list)
    incomes_categories = db.ListField(db.StringField(), default=constants.INCOMES_CATEGORIES)

    expenses = db.ListField(db.EmbeddedDocumentField(MoneyEntry), default=list)
    expenses_categories = db.ListField(db.StringField(), default=constants.EXPENSES_CATEGORIES)

    settings = db.EmbeddedDocumentField(Settings, default=Settings)
