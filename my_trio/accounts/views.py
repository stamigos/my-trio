from hashlib import sha1
import random

from flask import flash, render_template, request, redirect, url_for, Blueprint, g, abort
from peewee import IntegrityError, datetime as peewee_datetime
from flask.ext.mail import Message
from flask.ext.babel import gettext

from my_trio import app, recaptcha, mail
from my_trio import babel
from my_trio.models import Account, db
from my_trio.accounts.forms import RegistrationForm
from my_trio.utils import check_password_strength
from my_trio.utils import get_random_string
from config import MAIL_USERNAME
from auth import CustomAuth


auth = CustomAuth(app, db, user_model=Account)

random = random.SystemRandom()

register_page = Blueprint('register', __name__, template_folder="templates", url_prefix='/')


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


@app.route('/<lang_code>/', methods=['GET', 'POST'])
def index():
    user = auth.get_logged_in_user()

    if user is None:
        return render_template('index.html',
                               create_url=url_for('register', lang_code=g.current_lang),
                               login_url=url_for('login', lang_code=g.current_lang))
    if request.method == 'POST':
        if user.last_log_in is None:
            password = request.form['password']
            repeat_password = request.form['password_repeat']
            keyword = request.form['keyword']

            if password != repeat_password:
                flash(gettext("Password's mismatch"))
            else:
                if check_password_strength(user.email, password):
                    hashed_password = sha1(password).hexdigest()
                    user.password = hashed_password
                    user.keyword = keyword
                    user.last_log_in = peewee_datetime.datetime.now()
                    user.save()
                    flash(gettext("Password changed"))

    if user.last_log_in:
        user.last_log_in = peewee_datetime.datetime.now()

    return render_template('index.html',
                           first_login=str(user.last_log_in),
                           logout_url=url_for('logout', lang_code=g.current_lang))


@app.route('/<lang_code>/rules/')
def rules():
    return render_template('rules.html', lang_code=g.current_lang)


@app.route('/<lang_code>/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form['email']:
        try:
            user = Account.select().where(Account.email == request.form['email']).get()
        except Account.DoesNotExist:
            abort(404)
        password = sha1(request.form['password']).hexdigest()

        if user and user.password == password:
            auth.login_user(user)
            if user.last_log_in:
                user.last_log_in = peewee_datetime.datetime.now()
            user.save()
            flash(gettext('Logged in successfully.'))
            return redirect(request.args.get('next') or
                            url_for('index', lang_code=g.current_lang))
        else:
            flash(gettext('Email or password incorrect'))
            if not user:
                abort(404)

    return render_template('login.html',
                           url_register=url_for('register', lang_code=g.current_lang),
                           url_login=url_for('login', lang_code=g.current_lang))


@app.route('/<lang_code>/logout/')
def logout():
    auth.logout_user()
    return redirect(url_for('index', lang_code=g.current_lang))


@app.route('/<lang_code>/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        if recaptcha.verify():
            try:
                with db.transaction():
                    email = form.email.data
                    password = get_random_string()
                    msg = Message("Hello", sender=MAIL_USERNAME,
                                  recipients=[email])
                    account = Account.create(
                        email=email, password=sha1(password).hexdigest()
                    )
                    msg.subject = gettext("Welcome")
                    msg.html = render_template("registration_complete.html",
                                               password=password,
                                               url_login=url_for('login', lang_code=g.current_lang, _external=True))
                    mail.send(msg)
                    flash(gettext('Successfully registered! Check your email.'))

            except IntegrityError:
                    flash(gettext('That email is already taken'))
            return redirect(url_for('register', lang_code=g.current_lang))
        else:
            if not recaptcha.verify():
                flash(gettext('Recaptcha failed'))
    if request.method == 'POST' and not form.accept_tos.data:
        flash(gettext('You should accept the TOS'))
    return render_template('register.html', form=form,
                           url_register=url_for('register', lang_code=g.current_lang),
                           url_login=url_for('login', lang_code=g.current_lang))