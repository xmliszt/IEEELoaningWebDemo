from flask import Blueprint, render_template, redirect, url_for, flash, session
from utils.auth import is_login


confirm_api = Blueprint("confirm_api", __name__)

@confirm_api.route('/confirm')
def confirm():
    logged_in = is_login()
    if logged_in:
        student_id = session['id']
        return render_template('confirm.html', id=student_id)
    else:
        flash("Please login first!")
        return redirect(url_for('login_api.login'))