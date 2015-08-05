# -*- coding: utf-8 -*-
from hashlib import sha1
import traceback


from flask import request
from peewee import datetime as peewee_datetime

from my_trio.models import AccountLog, ErrorLog
from my_trio import log
from my_trio.constants import OperationType
from my_trio.utils import check_password_strength


class ServiceException(Exception):
    pass


class IndexController:
    def __init__(self, request):
        self.request = request
        self.log = log
        self.db_logger = AccountLog(request_ip=request.remote_addr,
                                    request_url=request.url,
                                    request_headers=request.headers,
                                    operation_type=OperationType.Index)

    def call(self, account, form):
        try:
            self._is_first_login(account, form)
            return dict(account=account, message="Success", result=True)
        except ServiceException, ex:
            self.log.warn("[operation_type: %i, error: %s, request_ip: %s, "
                          "request_url: %s, request_headers: %s]" %
                          (OperationType.Index, ex.message, request.remote_addr,
                           request.url, dict(request.headers.items())))
            self.db_logger.error = ex.message
            return dict(account=account, message=ex.message, result=False)
        except Exception, ex:
            self.log.exception("Index unexpected error")
            self.db_logger.error = ex.message
            # логируем в ErrorLog
            ErrorLog.create(request_data=request.data,
                            request_ip=request.remote_addr,
                            request_url=request.url,
                            request_method=request.method,
                            error=ex.message,
                            traceback=traceback.format_exc())
            return dict(account=account, message=ex.message, result=False)
        finally:
            self.db_logger.save()

    def _verify_password(self, form):
        if not form['password']:
            raise ServiceException('Password required')

    def _verify_password_repeat(self, form):
        if not form['password_repeat']:
            raise ServiceException('Repeat password required')

    def _is_first_login(self, account, form):
        # пользователь зашел впервые - предоставляем форму задания пароля
        if account.last_log_in is None:
            password = form['password']
            repeat_password = form['password_repeat']
            keyword = form['keyword']
            error = check_password_strength(account.email, password)
            if password != repeat_password:
                raise ServiceException("Password's mismatch")
            else:
                if error is None:
                    hashed_password = sha1(password).hexdigest()
                    account.password = hashed_password
                    account.keyword = keyword
                    account.last_log_in = peewee_datetime.datetime.now()
                    account.save()
                else:
                    raise ServiceException(error)

