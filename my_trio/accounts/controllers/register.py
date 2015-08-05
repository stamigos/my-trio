# -*- coding: utf-8 -*-
from hashlib import sha1
import traceback

from flask import render_template, request, url_for, g
from flask.ext.mail import Message
from flask.ext.babel import gettext

from my_trio import app, mail
from my_trio.models import Account, AccountLog, db, ErrorLog
from my_trio.utils import get_random_string
from my_trio import log
from config import MAIL_USERNAME
from my_trio.constants import OperationType


class ServiceException(Exception):
    pass


class RegistrationController:
    def __init__(self, request):
        self.request = request
        self.log = log
        self.db_logger = AccountLog(request_ip=request.remote_addr,
                                    request_url=request.url,
                                    request_headers=request.headers,
                                    operation_type=OperationType.Registration)

    def call(self, form, recaptcha):
        account = None
        try:
            self._verify_recaptcha(recaptcha)
            self._verify_tos(form)
            email = self._verify_email(form)
            password = get_random_string()
            account = self._create_account_db(email, password)
            return dict(account=account, message="Success", result=True)
        except ServiceException, ex:
            self.log.warn("[operation_type: %i, error: %s, request_ip: %s, "
                          "request_url: %s, request_headers: %s]" %
                          (OperationType.Index, ex.message, request.remote_addr,
                           request.url, dict(request.headers.items())))
            self.db_logger.error = ex.message
            return dict(account=account, message=ex.message, result=False)
        except Exception, ex:
            self.log.exception("Registration unexpected error")
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

    def _verify_recaptcha(self, recaptcha):
        if not recaptcha.verify():
            raise ServiceException("Recaptcha verification failed")

    def _verify_tos(self, form):
        if not form.accept_tos.data:
            raise ServiceException("TOS accept required")

    def _verify_email(self, form):
        if not form.email.data:
            raise ServiceException("Email required")

        try:
            Account.get(Account.email == form.email.data)
            # или возвращать объект account, предлагать восстановить пароль
            raise ServiceException("Email already registered")
        except Account.DoesNotExist:
            return form.email.data

    def _create_account(self, email, password):
        return Account.create(email=email, password=sha1(password).hexdigest())

    def _create_account_db(self, email, password):
        with db.transaction():
            account = self._create_account(email, password)
            self.db_logger.account = account
            if not self._send_email(email, password):
                db.transaction().rollback()
            else:
                return account

    def _send_email(self, email, password):
        try:
            # send email
            msg = Message("Hello", sender=MAIL_USERNAME,
                          recipients=[email])
            msg.subject = gettext("Welcome")
            msg.html = render_template("registration_complete.html",
                                       password=password,
                                       url_login=url_for('login',
                                                         lang_code=g.current_lang,
                                                         _external=True))
            with app.app_context():
                mail.send(msg)

            return True

        except Exception, ex:
            self.log.exception("Error while sending email to %s" % email)
            raise ServiceException("Sending email error: %s" % str(ex))
