# -*- coding: utf8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# configure our database
DATABASE = {
    'name': 'trio_db.db',
    'engine': 'peewee.SqliteDatabase',
}

DB_CONFIG = dict(database="trio_db", user="trio_user",
                 password=" ", host="localhost", port=5432,
                 max_connections=None, stale_timeout=600,
                 register_hstore=False, server_side_cursors=False)


# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# email server
MAIL_SERVER = 'smtp.gmail.com'  # your mailserver
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "test.mytrio@gmail.com"
MAIL_PASSWORD = "mytesttrio111"

# available languages
LANGUAGES = {
    'en': 'English',
    'ru': 'Russian',
    'uk_UA': 'Ukrainian'
}

# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = ''  # enter your MS translator app id here
MS_TRANSLATOR_CLIENT_SECRET = ''  # enter your MS translator app secret here

# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE = 50
MAX_SEARCH_RESULTS = 50