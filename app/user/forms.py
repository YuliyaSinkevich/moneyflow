from flask_wtf import FlaskForm
from wtforms.fields import StringField, FloatField, DateTimeField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange
from datetime import datetime
import app.constants as constants

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'


class MoneyEntryForm(FlaskForm):
    date = DateTimeField(u'Date:', validators=[InputRequired()], format=DATE_JS_FORMAT, default=datetime.now)
    category = SelectField(u'Category:', coerce=int, validators=[InputRequired()])
    value = FloatField(u'Value:', validators=[InputRequired(), NumberRange(min=0.01, message=u'Invalid value')])
    currency = StringField(u'Currency:', validators=[InputRequired()], default=constants.DEFAULT_CURRENCY)
    description = StringField(u'Description:')
    submit = SubmitField(u'Confirm')
