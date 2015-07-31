from flask import session, g, flash
from flask_peewee.auth import Auth


class CustomAuth(Auth):
    def get_logged_in_user(self):
        if session.get('logged_in'):
            if getattr(g, 'user', None):
                    return g.user

            try:
                return self.User.select().where(
                    self.User.id == session.get('user_pk')
                ).get()
            except self.User.DoesNotExist:
                pass

    def login_user(self, user):
        session['logged_in'] = True
        session['user_pk'] = user.get_id()
        session.permanent = True
        g.user = user
        flash('You are logged in as %s' % user.email, 'success')