# -*- coding: utf8 -*-
import os
import logging
from my_trio.utils import Struct
from datetime import date

basedir = os.path.abspath(os.path.dirname(__file__))

HOME_DIR = os.path.expanduser("~/PycharmProjects")
LOG_TO = os.path.join(HOME_DIR, "my-trio/logs")
TMP_DIR = os.path.join(HOME_DIR, "my-trio/tmp")


CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

GOOGLE_KEY = "6LfB4AkTAAAAAN1AKCBeT0YNme3gLK66WYkuwIb4"
GOOGLE_SECRET_KEY = "6LfB4AkTAAAAAIs-7bsnz_uBm40c0YdfNuR-eseu"

LOGGER = Struct(
    level=logging.DEBUG,
    file="account_log_{date:%Y-%m-%d}.log".format(date=date.today()),
    formatter=logging.Formatter("%(asctime)s [%(thread)d:%(threadName)s] "
                                "[%(levelname)s] - %(name)s:%(message)s"),
    peewee_file="account_peewee_log_{date:%Y-%m-%d}.log".format(date=date.today())
)


DB_CONFIG = dict(database="trio_db", user="trio_user",
                 password=" ", host="localhost", port=5432,
                 max_connections=None, stale_timeout=600,
                 register_hstore=False, server_side_cursors=False)


# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# email server
MAIL_SERVER = "mail.pay-trio.com"  # your mailserver
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "team@pay-trio.com"
MAIL_PASSWORD = "20pwteam15"

# available languages
LANGUAGES = {
    'en': 'English',
    'ru': 'Russian',
    'uk_UA': 'Ukrainian'
}

# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE = 50
MAX_SEARCH_RESULTS = 50