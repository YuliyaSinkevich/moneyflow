from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, current_user
from flask_mail import Message
from flask_babel import gettext

from werkzeug.security import generate_password_hash, check_password_hash

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from app import app, login_manager, mail, babel
import app.utils as utils
from app.home import home
import app.constants as constants
from app.home.user_loging_manager import User

from .forms import SignupForm, SigninForm

CONFIRM_LINK_TTL = 3600
SALT_LINK = 'email-confirm'

confirm_link_generator = URLSafeTimedSerializer(app.config['SECRET_KEY'])


def flash_success(text: str):
    flash(text, 'success')


def flash_error(text: str):
    flash(text, 'danger')


# routes

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


@home.route('/')
def start():
    languages = constants.AVAILABLE_LOCALES_PAIRS
    return render_template('index.html', languages=languages)


@home.route('/language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(url_for('home.start'))


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
        return render_template('home/login.html', form=form)

    check_user = User.objects(email=form.email.data).first()
    if not check_user:
        flash_error(gettext(u'User not found.'))
        return render_template('home/login.html', form=form)

    if check_user.status == User.Status.NO_ACTIVE:
        flash_error(gettext(u'User not active.'))
        return render_template('home/login.html', form=form)

    if not check_password_hash(check_user['password'], form.password.data):
        flash_error(gettext(u'Invalid password.'))
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


@home.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('home/register.html', form=form)

        email = form.email.data
        if not utils.is_valid_email(email, False):
            flash_error(gettext(u'Invalid email.'))
            return render_template('home/register.html', form=form)

        existing_user = User.objects(email=email).first()
        if existing_user:
            return redirect(url_for('home.login'))

        hash_pass = generate_password_hash(form.password.data, method='sha256')
        new_user = User(email=email, password=hash_pass)
        new_user.save()

        token = confirm_link_generator.dumps(email, salt=SALT_LINK)

        confirm_url = url_for('home.confirm_email', token=token, _external=True)
        config = app.config['PUBLIC_CONFIG']
        html = render_template('home/email/activate.html', confirm_url=confirm_url,
                               contact_email=config['support']['contact_email'], title=config['site']['title'],
                               company=config['company']['title'])
        msg = Message(subject=gettext(u'Confirm Email'), recipients=[email], html=html)
        mail.send(msg)
        flash_success(gettext(u'Please check email: {0}.'.format(email)))
        return redirect(url_for('home.login'))

    return render_template('home/register.html', form=form)


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    if current_user and current_user.is_authenticated:
        return current_user.settings.locale

    if session.get('language'):
        return session['language']

    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(constants.AVAILABLE_LOCALES)
