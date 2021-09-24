import unittest
from datetime import timedelta, date
from typing import Callable
from unittest.mock import patch

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
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={}) as mock:
            self.manager.validate_token("token")
            self.assertIsNone(self.manager.user)
        mock.assert_called_once_with("token")

        # Test a new user
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={"user_id": "NEW_FB_ID", "name": "FIRST MIDDLE LAST", "email": "EMAIL", "picture": "PICTURE"}):
            with patch.object(self.manager.dao, "get_user_by_firebase_id", return_value=None):
                self.manager.validate_token("")
                self.assertIsNotNone(self.manager.user)
                self.assertIsNotNone(self.manager.user.user_id)
                self.assertEqual("NEW_FB_ID", self.manager.user.firebase_id)
                self.assertEqual("FIRST", self.manager.user.first_name)
                self.assertEqual("MIDDLE LAST", self.manager.user.last_name)
                self.assertEqual("PICTURE", self.manager.user.image_url)

        # Test a saved user
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={"user_id": "NEW_FB_ID", "name": "FIRST MIDDLE LAST", "email": "EMAIL", "picture": "PICTURE"}):
            with patch.object(self.manager.dao, "get_user_by_firebase_id", return_value=None):
                with patch.object(self.manager.dao, "create_user", return_value=None) as create_user_mock:
                    self.manager.validate_token("")
                    self.assertIsNotNone(self.manager.user)
                create_user_mock.assert_called_once()

    def test_get_players(self):
        self.assert_requires_auth(lambda: self.manager.get_players())

        self.manager.user = Test.test_user
        expected_players = [Player("player_id", "owner_user_id", "image_url", "first_name", "last_name", "dominant_hand", "notes", "phone_number", "email", 5.0)]
        with patch.object(self.manager.dao, "get_players", return_value=expected_players):
            players = self.manager.get_players()
            self.assertEqual(expected_players, players)

    def assert_requires_auth(self, fun: Callable):
        self.manager.user = None
        with self.assertRaises(ServiceException) as e:
            fun()
        self.assertEqual(401, e.exception.status_code)
        self.assertEqual("Unable to authenticate", e.exception.error_message)


class MockFirebaseClient:
    def get_firebase_user(self, token):
        pass


class MockDao:
    def get_user(self, user_id: str) -> User: pass

    def get_user_by_firebase_id(self, firebase_id: str) -> Optional[User]: pass

    def create_user(self, user): pass

    def get_players(self): pass
