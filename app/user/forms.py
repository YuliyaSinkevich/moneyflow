from datetime import datetime

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.fields import StringField, FloatField, DateTimeField, SubmitField, SelectField, IntegerField
from wtforms.validators import InputRequired, NumberRange

import app.utils as utils
import app.constants as constants
from app.home.money_entry import MoneyEntry
from app.home.settings import Settings


class MoneyEntryForm(FlaskForm):
    type = IntegerField(lazy_gettext(u'Type:'), default=MoneyEntry.Type.INCOME)
    date = DateTimeField(lazy_gettext(u'Date:'), validators=[InputRequired()], format=constants.DATE_JS_FORMAT,
                         default=datetime.now)
    category = SelectField(lazy_gettext(u'Category:'), coerce=int, validators=[InputRequired()])
    value = FloatField(lazy_gettext(u'Value:'),
                       validators=[InputRequired(), NumberRange(min=0.01, message=lazy_gettext(u'Invalid value'))],
                       default=1.00)
    currency = StringField(lazy_gettext(u'Currency:'), validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    description = StringField(lazy_gettext(u'Description:'))
    recurring = SelectField(lazy_gettext(u'Recurring:'), coerce=int, validators=[InputRequired()],
                            choices=[(int(MoneyEntry.Recurring.SINGLE), lazy_gettext(u'Single')),
                                     (int(MoneyEntry.Recurring.EVERY_DAY), lazy_gettext(u'Every day')),
                                     (int(MoneyEntry.Recurring.EVERY_MONTH), lazy_gettext(u'Every month')),
                                     (int(MoneyEntry.Recurring.EVERY_YEAR), lazy_gettext(u'Every year'))],
                            default=MoneyEntry.Recurring.SINGLE)
    state = SelectField(lazy_gettext(u'State:'), coerce=int, validators=[InputRequired()],
                        choices=[(int(MoneyEntry.State.APPROVED), lazy_gettext(u'Approved')),
                                 (int(MoneyEntry.State.PENDING), lazy_gettext(u'Pending'))],
                        default=MoneyEntry.State.APPROVED)
    submit = SubmitField(lazy_gettext(u'Confirm'))

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
    locale = SelectField(lazy_gettext(u'Locale:'), coerce=str, validators=[InputRequired()],
                         choices=constants.AVAILABLE_LOCALES_PAIRS)
    currency = StringField(lazy_gettext(u'Currency:'), validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    start_date = DateTimeField(lazy_gettext(u'Start date:'), validators=[InputRequired()], format=constants.DATE_JS_FORMAT)
    end_date = DateTimeField(lazy_gettext(u'End date:'), validators=[InputRequired()], format=constants.DATE_JS_FORMAT)
    submit = SubmitField(lazy_gettext(u'Apply'))

    def make_settings(self):
        settings = Settings()
        return self.update_settings(settings)

    def update_settings(self, settings: Settings):
        settings.locale = self.locale.data
        settings.currency = self.currency.data

        settings.start_date = utils.stable_date(self.start_date.data)
        settings.end_date = utils.stable_date(self.end_date.data)
        return settings
