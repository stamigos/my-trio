from flask import flash, render_template, request, redirect, url_for, Blueprint, g, abort
from peewee import IntegrityError

from my_trio import app, recaptcha, mail
from my_trio import babel
from config import LANGUAGES
from my_trio.models import Account, db
from forms import RegistrationForm, LoginForm

from flask.ext.mail import Message
from flask.ext.babel import gettext
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from hashlib import sha1

import random

random = random.SystemRandom()

login_manager = LoginManager()
login_manager.init_app(app)

register_page = Blueprint('register', __name__, template_folder="templates", url_prefix='/')


@login_manager.user_loader
def load_user(userid):
    return Account(userid)


@app.before_request
def before():
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] not in ('en', 'ru', 'uk_UA'):
            return abort(404)
        g.current_lang = request.view_args['lang_code']
        request.view_args.pop('lang_code')


@babel.localeselector
def get_locale():
    return g.get('current_lang', 'en')


@app.route('/')
def root():
    return redirect(url_for('index', lang_code='en'))


@app.route('/<lang_code>', methods=['GET', 'POST'])
def index():
    # g.lang_code = lang_code
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] not in ('en', 'ru', 'uk_UA'):
            return abort(404)
        g.current_lang = request.view_args['lang_code']
        request.view_args.pop('lang_code')
    return render_template('index.html',
                           create_url=url_for('register', lang_code=g.current_lang),
                           login_url=url_for('login', lang_code=g.current_lang))


@app.route('/<lang_code>/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = LoginForm()
        if form.validate():
            user = Account.get(Account.email == form.email.data)
            if user and (user.password == sha1(request.form['password']).hexdigest()):
                login_user(user)
            else:
                flash(gettext('Username or password incorrect'))

            flash(gettext('Logged in successfully.'))

            next = request.args.get('next')
            if not next.is_valid(next):
                return abort(400)

            return redirect(next or url_for('index'))
    else:
        form = LoginForm()

    return render_template('login.html', form=form, url_register='/' + g.current_lang + '/register',
                           url_login='/' + g.current_lang + '/login')


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))


@app.route('/<lang_code>/register', methods=['GET', 'POST'])
def register():
    # g.lang_code = lang_code
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        if recaptcha.verify():
            try:
                with db.transaction():
                    email = form.email.data
                    password = get_random_string()
                    msg = Message("Hello", sender="test.trio@gmail.com",
                                  recipients=[email])
                    account = Account.create(
                        email=email, password=sha1(password).hexdigest()
                    )
                    # account.set_password(password)
                    msg.subject = gettext("Thanks for registering")
                    msg.html = render_template("registration_complete.html", password=password)
                    mail.send(msg)
                    flash(gettext('Successfully registered! Check your email.'))

            except IntegrityError:
                    flash(gettext('That email is already taken'))
            return redirect('/' + g.current_lang + '/register')
        else:
            if not recaptcha.verify():
                flash(gettext('Recaptcha failed'))
    return render_template('register.html', form=form, url_register='/' + g.current_lang + '/register',
                           url_login='/' + g.current_lang + '/login')