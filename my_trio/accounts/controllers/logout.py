# -*- coding: utf-8 -*-
from hashlib import sha1

from flask import request
from peewee import datetime as peewee_datetime
from my_trio.models import Account, AccountLog, db, ErrorLog

from my_trio import log
from my_trio.constants import OperationType
import traceback


class ServiceException(Exception):
    pass


class LogoutController:
    def __init__(self, request):
        self.request = request
        self.log = log
        self.db_logger = AccountLog(request_ip=request.remote_addr,
                                    request_url=request.url,
                                    request_headers=request.headers,
                                    operation_type=OperationType.Logout)

    def call(self, auth):
        try:
            auth.logout_user()
            return dict(message="Success", result=True)
        except ServiceException, ex:
            self.log.warn("[operation_type: %i, error: %s, request_ip: %s, "
                          "request_url: %s, request_headers: %s]" %
                          (OperationType.Index, ex.message, request.remote_addr,
                           request.url, dict(request.headers.items())))
            self.db_logger.error = ex.message
            return dict(message=ex.message, result=False)
        except Exception, ex:
            self.log.exception("Logout unexpected error")
            self.db_logger.error = ex.message
            # логируем в ErrorLog
            ErrorLog.create(request_data=request.data,
                            request_ip=request.remote_addr,
                            request_url=request.url,
                            request_method=request.method,
                            error=ex.message,
                            traceback=traceback.format_exc())
            return dict(message=ex.message, result=False)
        finally:
            self.db_logger.save()
