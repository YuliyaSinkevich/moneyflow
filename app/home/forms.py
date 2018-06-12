from flask_wtf import FlaskForm
from flask_babel import gettext

from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email


class SignupForm(FlaskForm):
    email = StringField(gettext(u'Email:'),
                        validators=[InputRequired(), Email(message=gettext(u'Invalid email')), Length(max=30)])
    password = PasswordField(gettext(u'Password:'), validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(gettext(u'Sign Up'))


class SigninForm(FlaskForm):
    email = StringField(gettext(u'Email:'),
                        validators=[InputRequired(), Email(message=gettext(u'Invalid email')), Length(max=30)])
    password = PasswordField(gettext(u'Password:'), validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(gettext(u'Sign In'))
