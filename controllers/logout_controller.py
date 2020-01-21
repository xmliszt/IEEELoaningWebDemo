from flask import flash, redirect, url_for, Blueprint, session

logout_api = Blueprint("logout_api", __name__)


@logout_api.route('/logout')
def logout():
    session['name'] = ""
    session['login'] = False
    session['member'] = ""
    session['id'] = ""
    session['admin'] = False

    flash("You have been logged out!")
    return redirect(url_for('login_api.login'))
