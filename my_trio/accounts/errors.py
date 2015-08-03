from flask import Blueprint, render_template, request
from my_trio.models import ErrorLog
from my_trio import log
from peewee import datetime as peewee_datetime

error_page = Blueprint('errors', __name__, template_folder="templates")


@error_page.app_errorhandler(404)
def page_not_found(e):
    log.error('page not found')
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error="page not found",
                    traceback=request.headers,
                    created=peewee_datetime.datetime.now())
    return render_template('error_pages/404.html'), 404


@error_page.app_errorhandler(500)
def internal_server_error(e):
    log.error('internal server error')
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error="internal server error",
                    traceback=request.headers,
                    created=peewee_datetime.datetime.now())
    return render_template('error_pages/500.html'), 500


@error_page.app_errorhandler(403)
def access_denied(e):
    log.error('access denied')
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error="access denied",
                    traceback=request.headers,
                    created=peewee_datetime.datetime.now())
    return render_template('error_pages/403.html'), 403


@error_page.app_errorhandler(400)
def bad_request(e):
    log.error('bad request')
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error="bad request",
                    traceback=request.headers,
                    created=peewee_datetime.datetime.now())
    return render_template('error_pages/400.html'), 400