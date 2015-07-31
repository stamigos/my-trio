from flask import Blueprint, render_template


error_page = Blueprint('errors', __name__, template_folder="templates")


@error_page.app_errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'), 404


@error_page.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error_pages/500.html'), 500


@error_page.app_errorhandler(403)
def access_denied(e):
    return render_template('error_pages/403.html'), 403


@error_page.app_errorhandler(400)
def bad_request(e):
    return render_template('error_pages/400.html'), 400