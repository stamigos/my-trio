import logging
import os

from flask import Flask
from flask_recaptcha import ReCaptcha
from flask.ext.mail import Mail
from flask.ext.babel import Babel

from config import GOOGLE_KEY, GOOGLE_SECRET_KEY
import config
from utils import StructEncoder, Logger


app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
recaptcha = ReCaptcha(app)
mail = Mail(app)
babel = Babel(app)

app.json_encoder = StructEncoder

if not os.path.exists(config.LOG_TO):
    os.makedirs(config.LOG_TO)

if not os.path.exists(config.TMP_DIR):
    os.makedirs(config.TMP_DIR)

fh = logging.FileHandler(os.path.join(config.LOG_TO, config.LOGGER.file))
fh.setLevel(config.LOGGER.level)
fh.setFormatter(config.LOGGER.formatter)

pw_fh = logging.FileHandler(os.path.join(config.LOG_TO, config.LOGGER.peewee_file))
pw_fh.setLevel(config.LOGGER.level)
pw_fh.setFormatter(config.LOGGER.formatter)

peewee_log = Logger(pw_fh, "peewee")
log = Logger(fh, "My.trio")

log.info("Service started!")


recaptcha.init_app(app, GOOGLE_KEY, GOOGLE_SECRET_KEY)

from my_trio.accounts.views import register_page
from my_trio.accounts.errors import error_page
from my_trio.accounts import errors, views

app.register_blueprint(register_page)
app.register_blueprint(error_page)

