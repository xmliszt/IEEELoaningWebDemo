from flask import Flask
import os
from datetime import timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'A137SUTDr9WEIEEjmNSECRXRT'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=12)
app.config['TESTING'] = False

basedir = os.path.abspath(os.path.dirname(__file__))
