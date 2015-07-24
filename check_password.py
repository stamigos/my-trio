from flask import flash
from flask.ext.babel import gettext
import re


def check_password_strength(email, password):
    valid = True
    if len(password) >= 30:
        valid = False
        flash(gettext("Password's length can't be more than 30 symbols"))

    elif len(password) <= 8:
        valid = False
        flash(gettext("Password's length can't be less than 8 symbols"))

    if email == password:
        valid = False
        flash(gettext("Password can't be your email"))

    if not re.findall('(\d+)', password):
        valid = False
        flash(gettext("Password must have at least one digit"))

    if not re.findall(r'[A-Z]', password):
        valid = False
        flash(gettext("Password must have at least one uppercase letter"))

    if not re.findall(r'[a-z]', password):
        valid = False
        flash(gettext("Password must have at least one lowercase letter"))
    return valid