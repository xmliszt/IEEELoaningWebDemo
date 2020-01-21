from flask import Blueprint, flash, redirect, url_for, request, session, render_template
from utils.auth import hash_password
from utils.membership_utils import change_attribute_of_member, get_attribute_from_member
from firebase import fs
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import app
import utils.constants as c

reset_api = Blueprint("reset_api", __name__)
client = fs.get_client()
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@reset_api.route('/<serial>')
def validate_key(serial):
    """
    Key here is user's previous stored hashed password
    """
    try:
        result = serializer.loads(serial, salt='forgot-password', max_age=c.RECOVERY_LINK_MAX_AGE)
    except SignatureExpired:
        flash("Your recovery link has expired!", 'warn')
        return redirect(url_for('error_api.error'))

    _id = result['id']

    stored_key = get_attribute_from_member(client, _id, "password")

    key = result['pwd']

    if key == stored_key:
        session['reset'] = True
        return redirect(url_for('reset_api.reset'))
    else:
        flash("Invalid recovery link! We cannot verify you.", 'warn')
        return redirect(url_for('error_api.error'))


@reset_api.route('/reset', methods=['GET', 'POST'])
def reset():
    try:
        is_resetting = session['reset']
    except:
        is_resetting = False

    if is_resetting is False:
        flash('You are not authorized to enter this page!', 'warn')
        return redirect(url_for('error_api.error'))

    if request.method == "POST":
        stdid = request.form['student_id']
        newpwd = request.form['newpwd']

        if stdid == "" or newpwd == "":
            flash("Please do not leave blank!", "warn")
            return render_template('reset.html')

        hashed = hash_password(newpwd)
        status = change_attribute_of_member(client, stdid, "password", hashed)
        if status == -1:
            flash("Failed to update password in Firebase.")
            redirect(url_for('error_api.error'))
        flash("Password has been updated!", "success")
        session['reset'] = False
        return render_template('reset.html')
    else:
        return render_template('reset.html')
