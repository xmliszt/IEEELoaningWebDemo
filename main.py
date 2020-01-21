from controllers.login_controller import login_api
from controllers.logout_controller import logout_api
from controllers.signup_controller import signup_api
from controllers.loan_controller import loan_api
from controllers.confirm_controller import confirm_api
from controllers.error_controller import error_api
from controllers.reset_controller import reset_api
from controllers.forgot_controller import forgot_api
from controllers.admin_controller import admin_api
from config import app
from flask import jsonify, session, send_from_directory
from datetime import timedelta
import os


app.register_blueprint(login_api)
app.register_blueprint(logout_api)
app.register_blueprint(signup_api)
app.register_blueprint(loan_api)
app.register_blueprint(confirm_api)
app.register_blueprint(error_api)
app.register_blueprint(reset_api)
app.register_blueprint(forgot_api)
app.register_blueprint(admin_api)


@app.before_first_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    :return: Http 200 response
    """
    return jsonify(success=True, status='IEEE SUTD Student Branch Website')


if __name__ == '__main__':
    app.run(debug=True)
