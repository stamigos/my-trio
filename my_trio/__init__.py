from flask import Flask
from flask_recaptcha import ReCaptcha
from flask.ext.mail import Mail
from flask.ext.babel import Babel

from config import GOOGLE_KEY, GOOGLE_SECRET_KEY


app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
recaptcha = ReCaptcha(app)
mail = Mail(app)
babel = Babel(app)

recaptcha.init_app(app, GOOGLE_KEY, GOOGLE_SECRET_KEY)

from my_trio.accounts.views import register_page
from my_trio.accounts.errors import error_page
from my_trio.accounts import errors, views

app.register_blueprint(register_page)
app.register_blueprint(error_page)