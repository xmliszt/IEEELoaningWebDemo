from flask import Blueprint, render_template, session, redirect, url_for, flash
from utils.auth import is_login


index_api = Blueprint("index_api", __name__)


@index_api.route('/')
@index_api.route('/home')
def index():

    logged_in = is_login()

    if logged_in:
        name = session['name']
        member = session['member']
        return render_template('index.html', name=name, member=member)
    else:
        flash("Please login first!")
        return redirect(url_for('login_api.login'))

