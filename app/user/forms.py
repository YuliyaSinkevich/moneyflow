from datetime import datetime

from flask_wtf import FlaskForm
from flask_babel import gettext

from wtforms.fields import StringField, FloatField, DateTimeField, SubmitField, SelectField, IntegerField
from wtforms.validators import InputRequired, NumberRange

import app.utils as utils
import app.constants as constants
from app.home.user_loging_manager import MoneyEntry, Settings


class MoneyEntryForm(FlaskForm):
    type = IntegerField(gettext(u'Type:'), default=MoneyEntry.Type.INCOME)
    date = DateTimeField(gettext(u'Date:'), validators=[InputRequired()], format=constants.DATE_JS_FORMAT,
                         default=datetime.now)
    category = SelectField(gettext(u'Category:'), coerce=int, validators=[InputRequired()])
    value = FloatField(gettext(u'Value:'),
                       validators=[InputRequired(), NumberRange(min=0.01, message=gettext(u'Invalid value'))],
                       default=1.00)
    currency = StringField(gettext(u'Currency:'), validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    description = StringField(gettext(u'Description:'))
    recurring = SelectField(gettext(u'Recurring:'), coerce=int, validators=[InputRequired()],
                            choices=[(int(MoneyEntry.Recurring.SINGLE), gettext(u'Single')),
                                     (int(MoneyEntry.Recurring.EVERY_DAY), gettext(u'Every day')),
                                     (int(MoneyEntry.Recurring.EVERY_MONTH), gettext(u'Every month')),
                                     (int(MoneyEntry.Recurring.EVERY_YEAR), gettext(u'Every year'))],
                            default=MoneyEntry.Recurring.SINGLE)
    submit = SubmitField(gettext(u'Confirm'))

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


class SettingsForm(FlaskForm):
    locale = SelectField(gettext(u'Locale:'), coerce=str, validators=[InputRequired()],
                         choices=constants.AVAILABLE_LOCALES_PAIRS)
    currency = StringField(gettext(u'Currency:'), validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    start_date = DateTimeField(gettext(u'Start date:'), validators=[InputRequired()], format=constants.DATE_JS_FORMAT)
    end_date = DateTimeField(gettext(u'End date:'), validators=[InputRequired()], format=constants.DATE_JS_FORMAT)
    submit = SubmitField(gettext(u'Apply'))

    def make_settings(self):
        settings = Settings()
        return self.update_settings(settings)

    def update_settings(self, settings: Settings):
        settings.locale = self.locale.data
        settings.currency = self.currency.data

        settings.start_date = utils.stable_date(self.start_date.data)
        settings.end_date = utils.stable_date(self.end_date.data)
        return settings
