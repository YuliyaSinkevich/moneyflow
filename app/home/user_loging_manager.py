from flask_login import UserMixin
from app import db
import datetime
from enum import IntEnum
from bson.objectid import ObjectId
import app.constants as constants


# revenues
# expenses


class MoneyEntry(db.EmbeddedDocument):
    id = db.ObjectIdField(required=True, default=ObjectId,
                          unique=True, primary_key=True)
    description = db.StringField(required=True)
    value = db.FloatField(required=True)
    currency = db.StringField(required=True)
    category = db.StringField(required=True)
    date = db.DateTimeField(default=datetime.datetime.now)


class Language(db.EmbeddedDocument):
    language = db.StringField(default=constants.DEFAULT_LANGUAGE)
    locale = db.StringField(default=constants.DEFAULT_LOCALE)


class Settings(db.EmbeddedDocument):
    currency = db.StringField(default=constants.DEFAULT_CURRENCY)
    language = Language()


class User(UserMixin, db.Document):
    class Status(IntEnum):
        NO_ACTIVE = 1
        ACTIVE = 2
        BANNED = 3

    meta = {'collection': 'users'}
    email = db.StringField(max_length=30, required=True)
    password = db.StringField(required=True)
    created_date = db.DateTimeField(default=datetime.datetime.now)
    status = db.IntField(default=Status.NO_ACTIVE)

    revenues = db.ListField(db.EmbeddedDocumentField(MoneyEntry), default=list)
    revenues_categories = db.ListField(db.StringField(), default=constants.REVENUES_CATEGORIES)

    expenses = db.ListField(db.EmbeddedDocumentField(MoneyEntry), default=list)
    expenses_categories = db.ListField(db.StringField(), default=constants.EXPENSES_CATEGORIES)

    settings = Settings()
