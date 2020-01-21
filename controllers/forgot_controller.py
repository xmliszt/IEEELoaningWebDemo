from flask import Blueprint, flash, request, render_template
from utils.membership_utils import get_attribute_from_member
from firebase import fs
from utils.email import send_email
from itsdangerous import URLSafeTimedSerializer
from config import app

forgot_api = Blueprint("forgot_api", __name__)
client = fs.get_client()
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@forgot_api.route('/forgot', methods=['POST','GET'])
def forgot():
    if request.method == 'POST':
        stdid = request.form['student_id']
        email = request.form['email']

        if stdid == "" or email == "":
            flash("Please do not leave blank!", 'warn')
            return render_template('forgot.html')

        stored_pwd = get_attribute_from_member(client, stdid, "password")

        _object = {
            'id': stdid,
            'pwd': stored_pwd
        }

        serialized = serializer.dumps(_object, "forgot-password")

        recovery_url = "https://ieeesutdweb.herokuapp.com/{}".format(serialized)
        recovery_msg = '''
        Hello,
        
        A request to reset your IEEE SUTD Loaning System account password was received. Click on the link below to reset your password and sign into your account.
        This link is valid for 10 minutes.
        
        {}
        
        You can safely disregard this email if you didn't request a password reset and your password will not be changed.
        
        Thanks.
        
        IEEE SUTD Student Branch
        IEEE Web Development Team
        
        Contact us: ieee@club.sutd.edu.sg
        [This is an auto-generated email. Please do not reply.]
        '''.format(recovery_url)

        status = send_email(recovery_msg, email)
        if status == -1:
            flash("Email was not sent due to network issue. Please try again later!", 'warn')
            return render_template('forgot.html')
        flash("A recovery link has been sent to your email. The link will be expired in 10 minutes.", 'success')
        return render_template('forgot.html')
    else:
        return render_template('forgot.html')
