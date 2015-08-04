from flask import Blueprint, render_template, request
from my_trio.models import ErrorLog
from my_trio import log
from peewee import datetime as peewee_datetime
import traceback

error_page = Blueprint('errors', __name__, template_folder="templates")


@error_page.app_errorhandler(404)
def page_not_found(e):
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error=e,
                    traceback=traceback.format_exc())
    return render_template('error_pages/404.html'), 404


@error_page.app_errorhandler(500)
def internal_server_error(e):
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error=e,
                    traceback=traceback.format_exc())
    return render_template('error_pages/500.html'), 500


@error_page.app_errorhandler(403)
def access_denied(e):
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error=e,
                    traceback=traceback.format_exc())
    return render_template('error_pages/403.html'), 403


@error_page.app_errorhandler(400)
def bad_request(e):
    ErrorLog.create(request_data=request.data,
                    request_ip=request.remote_addr,
                    request_url=request.url,
                    request_method=request.method,
                    error=e,
                    traceback=traceback.format_exc())
    return render_template('error_pages/400.html'), 400
