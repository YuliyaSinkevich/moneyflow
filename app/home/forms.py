from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import InputRequired, Length, Email


class SignupForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])

    eula = BooleanField(u'I did not read the terms and conditions',
                        validators=[InputRequired('You must agree to not agree!')])
    submit = SubmitField(u'Signup')


class SigninForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField(u'Signin')
