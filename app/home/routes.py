from flask import render_template, request, redirect, url_for
from flask_login import login_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from app.home import home
from app import login_manager
from app import mail
from app.home.user_loging_manager import User

CONFIRM_LINK_TTL = 3600
SALT_LINK = 'email-confirm'
SECRET = 'Thisisasecret!'

confirm_link_generator = URLSafeTimedSerializer(SECRET)


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class RegForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=3, max=20)])


@home.route('/')
def start():
    return render_template('index.html')


@home.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = confirm_link_generator.loads(token, salt=SALT_LINK, max_age=CONFIRM_LINK_TTL)
        confirm_user = User.objects(email=email).first()
        if confirm_user:
            confirm_user.status = User.Status.ACTIVE
            confirm_user.save()
            login_user(confirm_user)
            return redirect(url_for('home.login'))
        else:
            return '<h1>We can\'t find user.</h1>'
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'


@home.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = User.objects(email=form.email.data).first()
            if check_user and check_user.status != User.Status.NO_ACTIVE:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('user.dashboard'))

    return render_template('home/login.html', form=form)


@home.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            email = form.email.data
            existing_user = User.objects(email=email).first()
            if existing_user:
                return redirect(url_for('home.login'))

            hash_pass = generate_password_hash(form.password.data, method='sha256')
            User(email, hash_pass).save()

            token = confirm_link_generator.dumps(email, salt=SALT_LINK)
            msg = Message('Confirm Email', recipients=[email])
            link = url_for('home.confirm_email', token=token, _external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)
            return redirect(url_for('home.login'))

    return render_template('home/register.html', form=form)
