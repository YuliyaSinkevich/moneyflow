from datetime import datetime

from flask_wtf import FlaskForm

from wtforms.fields import StringField, FloatField, DateTimeField, SubmitField, SelectField, IntegerField
from wtforms.validators import InputRequired, NumberRange

import app.utils as utils
import app.constants as constants
from app.home.user_loging_manager import MoneyEntry


class MoneyEntryForm(FlaskForm):
    type = IntegerField(u'Type:', default=MoneyEntry.Type.INCOME)
    date = DateTimeField(u'Date:', validators=[InputRequired()], format=constants.DATE_JS_FORMAT, default=datetime.now)
    category = SelectField(u'Category:', coerce=int, validators=[InputRequired()])
    value = FloatField(u'Value:', validators=[InputRequired(), NumberRange(min=0.01, message=u'Invalid value')],
                       default=1.00)
    currency = StringField(u'Currency:', validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    description = StringField(u'Description:')
    recurring = SelectField(u'Recurring:', coerce=int, validators=[InputRequired()],
                            choices=[(int(MoneyEntry.Recurring.SINGLE), 'Single'),
                                     (int(MoneyEntry.Recurring.EVERY_DAY), 'Every day'),
                                     (int(MoneyEntry.Recurring.EVERY_MONTH), 'Every month'),
                                     (int(MoneyEntry.Recurring.EVERY_YEAR), 'Every year')],
                            default=MoneyEntry.Recurring.SINGLE)
    submit = SubmitField(u'Confirm')

    def __init__(self, categories: list, **kwargs):
        super(MoneyEntryForm, self).__init__(**kwargs)
        self.category.choices = categories

    def make_entry(self):
        entry = MoneyEntry()
        return self.update_entry(entry)

    def update_entry(self, entry: MoneyEntry):
        entry.type = self.type.data
        entry.description = self.description.data
        entry.value = self.value.data
        entry.currency = self.currency.data

        category_pos = self.category.data
        categories = self.category.choices
        entry.category = categories[category_pos][1]

        date = self.date.data
        entry.date = utils.stable_date(date)

        recurring_pos = self.recurring.data
        recurrings = self.recurring.choices
        entry.recurring = recurrings[recurring_pos][0]
        return entry
