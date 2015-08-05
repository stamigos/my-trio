import random

from flask import flash, render_template, request, redirect, url_for,\
    Blueprint, g, abort
from peewee import datetime as peewee_datetime
from flask.ext.babel import gettext

from my_trio import app, recaptcha
from my_trio import babel
from my_trio.models import Account, AccountLog, db
from my_trio.accounts.forms import RegistrationForm, ProfileForm
from auth import CustomAuth
from my_trio.decorators import jsonify_result
from my_trio.accounts.controllers.register import RegistrationController
from my_trio.accounts.controllers.login import LoginController
from my_trio.accounts.controllers.index import IndexController
from my_trio.accounts.controllers.logout import LogoutController

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


@app.route('/logs/account/')
@jsonify_result
def get_logs():
    def get_result(log_class):
        return {"logs": [l.to_dict() for l in list(log_class.select().order_by(log_class.created.desc()))]}
    return get_result(AccountLog)


@app.route('/<lang_code>/', methods=['GET', 'POST'])
def index():
    account = auth.get_logged_in_user()
    if request.method == 'GET':
        if account is None:
            return render_template('index.html',
                                   create_url=url_for('register', lang_code=g.current_lang),
                                   login_url=url_for('login', lang_code=g.current_lang))
        else:
            if account.last_log_in:
                account.last_log_in = peewee_datetime.datetime.now()
                account.save()
            return render_template('index.html',
                                   first_login=str(account.last_log_in),
                                   logout_url=url_for('logout', lang_code=g.current_lang),
                                   settings_url=url_for('settings', lang_code=g.current_lang))

    result = IndexController(request).call(account, request.form)

    if result['account'] and result['result']:
        flash(result['message'])
        return render_template('index.html',
                               first_login=str(account.last_log_in),
                               logout_url=url_for('logout', lang_code=g.current_lang),
                               settings_url=url_for('settings', lang_code=g.current_lang))
    else:
        flash(result['message'])
        return render_template('index.html',
                               first_login=str(account.last_log_in),
                               logout_url=url_for('logout', lang_code=g.current_lang),
                               settings_url=url_for('settings', lang_code=g.current_lang))


@app.route('/<lang_code>/settings/')
def settings():
    form = ProfileForm(request.form)
    return render_template('settings.html', form=form, lang_code=g.current_lang)


@app.route('/<lang_code>/rules/')
def rules():
    return render_template('rules.html', lang_code=g.current_lang)


@app.route('/<lang_code>/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',
                               url_register=url_for('register', lang_code=g.current_lang),
                               url_login=url_for('login', lang_code=g.current_lang))

    result = LoginController(request).call(request.form, auth)
    if result['account'] and result['result']:
        flash(result['message'])
        return redirect(url_for('index', lang_code=g.current_lang))
    else:
        flash(result['message'])
        return render_template('login.html',
                               url_register=url_for('register', lang_code=g.current_lang),
                               url_login=url_for('login', lang_code=g.current_lang))


@app.route('/<lang_code>/logout/')
def logout():
    result = LogoutController(request).call(auth)
    if result['result']:
        flash(result['message'])
        return redirect(url_for('index', lang_code=g.current_lang))
    else:
        flash(result['message'])
        return redirect(url_for('index', lang_code=g.current_lang))


@app.route('/<lang_code>/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == "GET" or not form.validate():
        return render_template('register.html', form=form,
                               url_register=url_for('register', lang_code=g.current_lang),
                               url_login=url_for('login', lang_code=g.current_lang))

    result = RegistrationController(request).call(form, recaptcha)

    if result['account'] and result['result'] == True:
        flash(result['message'])
        return redirect(url_for('login', lang_code=g.current_lang))
    else:
        flash(result['message'])
        return render_template('register.html', form=form,
                               url_register=url_for('register', lang_code=g.current_lang),
                               url_login=url_for('login', lang_code=g.current_lang))
