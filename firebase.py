import os
import firebase_admin
from firebase_admin import credentials, firestore


class Firestore:

    def __init__(self):
        _cert_path = os.path.join(os.getcwd(), "sutdieeeweb.json")
        cred = credentials.Certificate(_cert_path)
        _db = firebase_admin.initialize_app(cred)
        self.client = firestore.client(_db)

    def get_client(self):
        return self.client


fs = Firestore()