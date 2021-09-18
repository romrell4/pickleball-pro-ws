import unittest
from datetime import timedelta, date

from bl import Manager
from domain import *


class Test(unittest.TestCase):
    test_user = User("USER1", "FB_ID", "User", "One", "user.jpg")

    def setUp(self):
        self.manager = Manager(MockFirebaseClient(), MockDao())

    def test_validate_token(self):
        # Test without a token (unauthenticated request)
        self.manager.validate_token(None)
        self.assertIsNone(self.manager.user)

        # Test invalid token response
        self.manager.firebase_client.valid_user = False
        self.manager.validate_token("")
        self.assertIsNone(self.manager.user)

        # Test a new user
        self.manager.firebase_client.valid_user = True
        self.manager.validate_token("")
        self.assertIsNotNone(self.manager.user)
        self.assertTrue(self.manager.dao.created_user)
        self.assertIsNotNone(self.manager.user.user_id)
        self.assertEqual("NEW_FB_ID", self.manager.user.firebase_id)
        self.assertEqual("FIRST", self.manager.user.first_name)
        self.assertEqual("MIDDLE LAST", self.manager.user.last_name)
        self.assertEqual("PICTURE", self.manager.user.image_url)

        # Test a saved user
        self.manager.firebase_client.valid_user = True
        self.manager.validate_token("")
        self.assertIsNotNone(self.manager.user)
        self.assertFalse(self.manager.dao.created_user)


class MockFirebaseClient:
    valid_user = True

    def get_firebase_user(self, token):
        if self.valid_user:
            return {"user_id": "NEW_FB_ID", "name": "FIRST MIDDLE LAST", "email": "EMAIL", "picture": "PICTURE"}
        else:
            return {}


def create_date(day_offset):
    return date.today() + timedelta(days=day_offset)


class MockDao:
    user_database = {
        Test.test_user.user_id: Test.test_user,
        "TEST1": User("TEST1", "", "", "", ""),
        "BAD_USER": User("BAD_USER", "", "", "", "")
    }
    created_user = False

    def get_user(self, user_id: str) -> User:
        return self.user_database.get(user_id)

    def get_user_by_firebase_id(self, firebase_id: str) -> Optional[User]:
        self.created_user = False
        return next(iter([user for (user_id, user) in self.user_database.items() if user.firebase_id == firebase_id]), None)

    def create_user(self, user):
        self.user_database[user.user_id] = user
        self.created_user = True
        return user
