from flask_wtf import FlaskForm
from wtforms.fields import StringField, FloatField, DateTimeField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange
from datetime import datetime

import app.constants as constants
from app.home.user_loging_manager import MoneyEntry

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'


class MoneyEntryForm(FlaskForm):
    date = DateTimeField(u'Date:', validators=[InputRequired()], format=DATE_JS_FORMAT, default=datetime.now)
    category = SelectField(u'Category:', coerce=int, validators=[InputRequired()])
    value = FloatField(u'Value:', validators=[InputRequired(), NumberRange(min=0.01, message=u'Invalid value')],
                       default=1.00)
    currency = StringField(u'Currency:', validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    description = StringField(u'Description:')
    submit = SubmitField(u'Confirm')

    def __init__(self, categories: list, entry=MoneyEntry(), **kwargs):
        super(MoneyEntryForm, self).__init__(**kwargs)
        self.entry = entry

        extended_cat = []
        for index, value in enumerate(categories):
            extended_cat.append((index, value))

        self.category.choices = extended_cat

    def get_entry(self):
        self.entry.description = self.description.data
        self.entry.value = self.value.data
        self.entry.currency = self.currency.data
        category_pos = self.category.data
        categories = self.category.choices
        self.entry.category = categories[category_pos][1]
        data_str = self.date._value()
        self.entry.date = datetime.strptime(data_str, DATE_JS_FORMAT)
        return self.entry


class MoneyEditEntryForm(MoneyEntryForm):
    def __init__(self, categories: list, entry, **kwargs):
        super(MoneyEditEntryForm, self).__init__(categories, entry, **kwargs)

        category_index = 0
        for index, value in enumerate(categories):
            if entry.category == value:
                category_index = index

        self.date.data = entry.date
        self.category.data = category_index
        self.value.data = entry.value
        self.currency.data = entry.currency
        if entry.description:
            self.description.data = entry.description
