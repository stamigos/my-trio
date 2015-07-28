from flask import session, g
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