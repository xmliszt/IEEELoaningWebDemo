from flask import Blueprint, flash, redirect, url_for, request, session, render_template
from utils.auth import verify_password
from utils.membership_utils import get_attribute_from_member, attibutes_to_list
from firebase import fs
import datetime


login_api = Blueprint("login_api", __name__)
client = fs.get_client()


@login_api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        _usrname = request.form['username']
        _pwdword = request.form['password']

        if _usrname == "" or _pwdword == "":
            flash("Username or password is empty!")
            return redirect(url_for('login_api.login'))

        _stdid = attibutes_to_list(client, "student_id")

        if _usrname == "admin":
            if _pwdword == "1i1e2e3e2019":
                session['admin'] = True
                session['login'] = True
                session['name'] = 'admin'
                session['id'] = 'admin'
                session['member'] = 'admin'
                return redirect(url_for('admin_api.index'))
            else:
                flash("Wrong admin password! Entry not authorized!")
                return render_template('login.html')

        # invalid membership
        if _usrname not in _stdid:
            flash("Sorry! Seems like you haven't register for an account yet. Click 'Sign up' below to register first!")
            return redirect(url_for('login_api.login'))

        _end_date = get_attribute_from_member(client, _usrname, "end_date")
        _now = datetime.datetime.timestamp(datetime.datetime.now())
        _end = float(datetime.datetime.timestamp(datetime.datetime.strptime(_end_date, "%Y-%m-%d %H:%M:%S")))
        # expired membership
        if _end < _now:
            flash("Sorry! Seems like your membership has expired! Please renew and sign in using your new membership again!")
            return redirect(url_for('login_api.login'))

        _stored_pwd = get_attribute_from_member(client, _usrname, "password")

        # verify password
        if verify_password(_stored_pwd, _pwdword):
            session['name'] = get_attribute_from_member(client, _usrname, "name")
            session['member'] = get_attribute_from_member(client, _usrname, "membership")
            session['id'] = _usrname
            session['login'] = True
            session['admin'] = False

            return redirect(url_for('loan_api.loan'))
        else:
            flash("Wrong password. Please try again!")
            return redirect(url_for('login_api.login'))

    else:
        session['email'] = ""
        return render_template("login.html")
