# -*- coding: utf8 -*-

from peewee import Model, CharField, DateTimeField, BooleanField, datetime as peewee_datetime
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

    email = CharField(unique=True)
    registered_on = DateTimeField(default=peewee_datetime.datetime.now())
    password = CharField()
    active = BooleanField(default=True)
    first_login = BooleanField(default=True)  # check first user login
    keyword = CharField(max_length=70, null=True)  # keyword for restoring password
    description = CharField(null=True)

    def __unicode__(self):
        return self.email


def init_db():
    try:
        db.connect()
        map(lambda l: db.drop_table(l, True), [Account])
        print "tables dropped"
        db.create_tables([Account])
        print "tables created"
    except:
        db.rollback()
        raise