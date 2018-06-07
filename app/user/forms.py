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

    def __init__(self, categories: list, **kwargs):
        super(MoneyEntryForm, self).__init__(**kwargs)
        self.category.choices = categories

    def make_entry(self):
        entry = MoneyEntry()
        return self.update_entry(entry)

    def update_entry(self, entry: MoneyEntry):
        entry.description = self.description.data
        entry.value = self.value.data
        entry.currency = self.currency.data
        category_pos = self.category.data
        categories = self.category.choices
        entry.category = categories[category_pos][1]
        date = self.date.data
        entry.date = date.replace(microsecond=0)
        return entry
