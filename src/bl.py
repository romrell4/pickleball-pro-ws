from domain import User
from firebase_client import FirebaseClient
from da import Dao


class Manager:
    def __init__(self, firebase_client: FirebaseClient, dao: Dao):
        self.firebase_client = firebase_client
        self.dao = dao
        self.user = None

    def validate_token(self, token):
        if token is None: return

        try:
            firebase_user = self.firebase_client.get_firebase_user(token)
            # TODO: Use this log to determine what fields can come from the JWT
            print(firebase_user)
            self.user = self.dao.get_user_by_firebase_id(firebase_user["user_id"])
            if self.user is None:
                first_name, last_names = firebase_user["name"].split(" ", 1)
                self.user = User(firebase_user["user_id"], first_name, last_names, firebase_user.get("picture"))
                self.dao.create_user(self.user)
        except (KeyError, ValueError):
            self.user = None
