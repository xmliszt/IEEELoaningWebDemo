from flask import Blueprint, request, render_template, redirect, url_for, flash
from utils.auth import hash_password
from firebase import fs
from utils.membership_utils import change_attribute_of_member, get_attribute_from_member


signup_api = Blueprint("signup_api", __name__)
client = fs.get_client()


@signup_api.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":

        _student_id = request.form['student_id']
        _membership = request.form['membership']
        _pwd = request.form['password']

        _stored_pwd = get_attribute_from_member(client, _student_id, "password")
        membership_number = get_attribute_from_member(client, _student_id, "membership")

        if _membership == membership_number and _stored_pwd != "":
            flash("You have already signed up. Use your membership number as username to login!")
            return redirect(url_for('login_api.login'))

        if _membership != membership_number:
            flash("Sorry! Your membership number is invalid! Please check with IEEE Exco about "
                  "your membership status or click on the links below to sign up for official membership!")
            return render_template("signup.html")

        _hashedpwd = hash_password(_pwd)

        change_attribute_of_member(client, _student_id, "password", _hashedpwd)

        flash("You have been signed up successfully!")  # show in the login message place
        return redirect(url_for('login_api.login'))

    else:
        return render_template("signup.html")
