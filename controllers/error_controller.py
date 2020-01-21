from flask import Blueprint, render_template


error_api = Blueprint("error_api", __name__)


@error_api.route('/error')
def error():
    return render_template('error.html')