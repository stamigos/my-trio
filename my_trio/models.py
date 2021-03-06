# -*- coding: utf8 -*-

from peewee import Model, CharField, DateTimeField, TextField, IntegerField, datetime as peewee_datetime
from playhouse.pool import PooledPostgresqlExtDatabase
from flask_peewee.auth import BaseUser

from config import DB_CONFIG
from my_trio.utils import Struct


db = PooledPostgresqlExtDatabase(**DB_CONFIG)
db.commit_select = True
db.autorollback = True


class _Model(Model):
        class Meta:
            database = db

        def __repr__(self):
            #data = ", ".join(["%s: %s" % (key, unicode(value).encode('utf8') if value else None) for key, value in self._data.items()])
            #return "{class_name}: {{ {data} }}".format(class_name = self.__class__.__name__, data = data)
            return "{class_name}(id={id})".format(class_name=self.__class__.__name__, id=self.id)

        def to_dict(self):
            return dict(self._data.items())

        def to_struct(self):
            return Struct(**self.to_dict())

        def info(self):
            # TODO return short info for merchant
            return self.to_struct()

        @classmethod
        def get_by_id(cls, id):
            try:
                return cls.get(cls.id == id)
            except cls.DoesNotExist:
                return None

        def save(self, **kwds):
            with db.transaction() as txn:
                Model.save(self, **kwds)

        def delete_me(self):
            with db.transaction() as txn:
                self.delete_instance()


class Account(_Model, BaseUser):
    class Meta:
        db_table = "accounts"

    email = CharField(unique=True, max_length=320)
    registered_on = DateTimeField(default=peewee_datetime.datetime.now())
    password = CharField()
    last_log_in = DateTimeField(null=True)
    keyword = CharField(max_length=70, null=True)  # keyword for restoring password
    description = CharField(null=True)

    def __unicode__(self):
        return self.email


class AccountLog(_Model):
    class Meta:
        db_table = "account_logs"

    operation_type = IntegerField()
    error = TextField(null=True)
    request_ip = CharField()
    request_url = TextField()
    request_headers = TextField()
    created = DateTimeField(default=peewee_datetime.datetime.now)


class ErrorLog(_Model):
    class Meta:
        db_table = "error_logs"

    request_data = TextField()
    request_ip = CharField()
    request_url = CharField()
    request_method = CharField()
    error = TextField()
    traceback = TextField(null=True)
    created = DateTimeField(default=peewee_datetime.datetime.now)


def init_db():
    try:
        db.connect()
        map(lambda l: db.drop_table(l, True), [Account, AccountLog, ErrorLog])
        print "tables dropped"
        db.create_tables([Account, AccountLog, ErrorLog])
        print "tables created"
    except:
        db.rollback()
        raise
