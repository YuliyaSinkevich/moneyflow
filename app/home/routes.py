from flask import render_template, request, redirect, url_for, flash, current_app as app
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from .forms import SignupForm, SigninForm

import app.utils as utils

from app.home import home
from app import login_manager
from app import mail
from app.home.user_loging_manager import User

CONFIRM_LINK_TTL = 3600
SALT_LINK = 'email-confirm'
SECRET = 'Thisisasecret!'

confirm_link_generator = URLSafeTimedSerializer(SECRET)


def flash_success(text: str):
    flash(text, 'success')


def flash_error(text: str):
    flash(text, 'danger')


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash_error(u"Error in the %s field - %s" % (getattr(form, field).label.text, error))


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


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


def post_login(form: SigninForm):
    if not form.validate_on_submit():
        flash_errors(form)
        return render_template('home/login.html', form=form)

    check_user = User.objects(email=form.email.data).first()
    if not check_user:
        flash_error('User not found.')
        return render_template('home/login.html', form=form)

    if check_user.status == User.Status.NO_ACTIVE:
        flash_error('User not active.')
        return render_template('home/login.html', form=form)

    if not check_password_hash(check_user['password'], form.password.data):
        flash_error('Invalid password.')
        return render_template('home/login.html', form=form)

    login_user(check_user)
    return redirect(url_for('user.dashboard'))


@home.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = SigninForm()
    if request.method == 'POST':
        return post_login(form)

    return render_template('home/login.html', form=form)


@home.route('/private_policy')
def private_policy():
    config = app.config['PUBLIC_CONFIG']
    return render_template('home/private_policy.html', contact_email=config['support']['contact_email'],
                           title=config['site']['title'])


@home.route('/term_of_use')
def term_of_use():
    config = app.config['PUBLIC_CONFIG']
    return render_template('home/term_of_use.html', contact_email=config['support']['contact_email'],
                           title=config['site']['title'])


def post_register(form: SignupForm):
    if not form.validate_on_submit():
        flash_errors(form)
        return render_template('home/register.html', form=form)

    email = form.email.data
    if not utils.is_valid_email(email, False):
        flash_error('Invalid email.')
        return render_template('home/register.html', form=form)

    existing_user = User.objects(email=email).first()
    if existing_user:
        return redirect(url_for('home.login'))

    hash_pass = generate_password_hash(form.password.data, method='sha256')
    new_user = User(email, hash_pass)
    new_user.save()

    token = confirm_link_generator.dumps(email, salt=SALT_LINK)
    msg = Message('Confirm Email', recipients=[email])
    link = url_for('home.confirm_email', token=token, _external=True)
    msg.body = 'Your link is {}'.format(link)
    mail.send(msg)
    flash_success('Please check email:{0}.'.format(email))
    return redirect(url_for('home.login'))


@home.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if request.method == 'POST':
        return post_register(form)

    return render_template('home/register.html', form=form)
