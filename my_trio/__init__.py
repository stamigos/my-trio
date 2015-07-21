from flask import Flask, Blueprint
from flask_recaptcha import ReCaptcha
from flask.ext.mail import Mail
from flask.ext.babel import Babel

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
recaptcha = ReCaptcha(app)
mail = Mail(app)
babel = Babel(app)

recaptcha.init_app(app, "6LfB4AkTAAAAAN1AKCBeT0YNme3gLK66WYkuwIb4", "6LfB4AkTAAAAAIs-7bsnz_uBm40c0YdfNuR-eseu")

from accounts.views import register_page

app.register_blueprint(register_page)