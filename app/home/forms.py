from flask_wtf import FlaskForm

from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email


class SignupForm(FlaskForm):
    email = StringField(u'Email:', validators=[InputRequired(), Email(message=u'Invalid email'), Length(max=30)])
    password = PasswordField(u'Password:', validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(u'Sign Up')


class SigninForm(FlaskForm):
    email = StringField(u'Email:', validators=[InputRequired(), Email(message=u'Invalid email'), Length(max=30)])
    password = PasswordField(u'Password:', validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(u'Sign In')
