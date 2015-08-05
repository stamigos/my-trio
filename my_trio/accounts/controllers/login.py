# -*- coding: utf-8 -*-
from hashlib import sha1
import traceback

from flask import request
from peewee import datetime as peewee_datetime

from my_trio.models import Account, AccountLog, ErrorLog
from my_trio import log
from my_trio.constants import OperationType


class ServiceException(Exception):
    pass


class LoginController:
    def __init__(self, request):
        self.request = request
        self.log = log
        self.db_logger = AccountLog(request_ip=request.remote_addr,
                                    request_url=request.url,
                                    request_headers=request.headers,
                                    operation_type=OperationType.Login)

    def call(self, form, auth):
        account = None
        try:
            account = self._verify_account(form)
            password = sha1(form['password']).hexdigest()
            self._verify_password(form)
            self._check_password(account, password)
            auth.login_user(account)
            self._set_last_login(account)
            return dict(account=account, message="Success", result=True)
        except ServiceException, ex:
            self.log.warn("[operation_type: %i, error: %s, request_ip: %s, "
                          "request_url: %s, request_headers: %s]" %
                          (OperationType.Index, ex.message, request.remote_addr,
                           request.url, dict(request.headers.items())))
            self.db_logger.error = ex.message
            return dict(account=account, message=ex.message, result=False)
        except Exception, ex:
            self.log.exception("Login unexpected error")
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
            raise ServiceException("Password required")

    def _verify_account(self, form):
        if not form['email']:
            raise ServiceException("Email required")

        try:
            account = Account.get(Account.email == form['email'])
            return account
        except Account.DoesNotExist:
            raise ServiceException('Account does not exist')

    def _check_password(self, account, password):
        if account.password != password:
            raise ServiceException('Password incorrect')

    def _set_last_login(self, account):
        if account.last_log_in:
            account.last_log_in = peewee_datetime.datetime.now()
            account.save()
