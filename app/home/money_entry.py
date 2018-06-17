from datetime import datetime
from enum import IntEnum

from bson.objectid import ObjectId

from app import db
import app.constants as constants


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

    class State(IntEnum):
        PENDING = 0,
        APPROVED = 1

    id = db.ObjectIdField(required=True, default=ObjectId,
                          unique=True, primary_key=True)
    type = db.IntField(required=True, default=Type.INCOME)
    description = db.StringField(required=True)
    value = db.FloatField(required=True, default=1.00)
    currency = db.StringField(required=True, default=constants.DEFAULT_CURRENCY)
    category = db.StringField(required=True)
    date = db.DateTimeField(required=True, default=datetime.now)
    recurring = db.IntField(default=Recurring.SINGLE)
    state = db.IntField(required=True, default=State.APPROVED)

    def clone(self):
        entry = MoneyEntry()
        entry.type = self.type
        entry.description = self.description
        entry.value = self.value
        entry.currency = self.currency
        entry.category = self.category
        entry.date = self.date
        entry.recurring = self.recurring
        entry.state = self.state
        return entry
