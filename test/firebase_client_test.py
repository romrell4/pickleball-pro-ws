import os
import unittest

from firebase_admin.auth import InvalidIdTokenError

from test import properties
from firebase_client import FirebaseClientImpl

class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../src/firebase_creds.json"
        cls.client = FirebaseClientImpl()

    def test_validate_token(self):
        # Test empty token
        self.assertRaises(ValueError, lambda: self.client.get_firebase_user(""))

        # Test partially correct format
        self.assertRaises(InvalidIdTokenError, lambda: self.client.get_firebase_user("a.bad.token"))

        # Test valid but old
        self.assertRaises(InvalidIdTokenError, lambda: self.client.get_firebase_user(properties.old_firebase_token))

        # In order to run this test, you'll have to generate a new valid token and place it in the properties file
        user = self.client.get_firebase_user(properties.valid_firebase_token)
        self.assertIsNotNone(user)
        print(user)
