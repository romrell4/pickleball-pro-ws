from typing import Optional

import firebase_admin
from firebase_admin import auth


class FirebaseClient:
    @staticmethod
    def get_firebase_user(token: Optional[str]): pass


class FirebaseClientImpl(FirebaseClient):
    def __init__(self):
        firebase_admin.initialize_app()

    @staticmethod
    def get_firebase_user(token: Optional[str]):
        return auth.verify_id_token(token)
