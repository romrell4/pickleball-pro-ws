import unittest
from typing import Callable
from unittest.mock import patch

from bl import ManagerImpl
from da import Dao
from domain.exceptions import ServiceException
from firebase_client import FirebaseClient
from test import fixtures


class Test(unittest.TestCase):
    def setUp(self):
        self.manager = ManagerImpl(FirebaseClient(), Dao())

    def test_validate_token(self):
        # Test without a token (unauthenticated request)
        self.manager.validate_token(None)
        self.assertIsNone(self.manager.user)

        # Test when firebase throws an error (invalid token)
        def raise_error(_): raise ValueError()

        with patch.object(self.manager.firebase_client, "get_firebase_user", side_effect=raise_error):
            self.manager.validate_token(None)
            self.assertIsNone(self.manager.user)

        # Test invalid token response
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={}) as mock:
            self.manager.validate_token("token")
            self.assertIsNone(self.manager.user)
        mock.assert_called_once_with("token")

        # Test a new user with an empty name
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={"user_id": "NEW_FB_ID", "name": "", "email": "EMAIL", "picture": "PICTURE"}):
            with patch.object(self.manager.dao, "get_user_by_firebase_id", return_value=None):
                self.manager.validate_token("")
                self.assertIsNotNone(self.manager.user)
                self.assertIsNotNone(self.manager.user.user_id)
                self.assertEqual("NEW_FB_ID", self.manager.user.firebase_id)
                self.assertEqual("", self.manager.user.first_name)
                self.assertEqual("", self.manager.user.last_name)
                self.assertEqual("PICTURE", self.manager.user.image_url)

        # Test a new user
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={"user_id": "NEW_FB_ID", "name": "FIRST MIDDLE LAST", "email": "EMAIL", "picture": "PICTURE"}):
            with patch.object(self.manager.dao, "get_user_by_firebase_id", return_value=None):
                with patch.object(self.manager.dao, "create_user") as create_user_mock:
                    with patch.object(self.manager.dao, "create_player") as create_player_mock:
                        self.manager.validate_token("")
                        self.assertIsNotNone(self.manager.user)

                create_user_mock.assert_called_once()
                user = create_user_mock.call_args.args[0]
                self.assertEqual("NEW_FB_ID", user.firebase_id)
                self.assertEqual("FIRST", user.first_name)
                self.assertEqual("MIDDLE LAST", user.last_name)
                self.assertEqual("PICTURE", user.image_url)

                create_player_mock.assert_called_once()
                player = create_player_mock.call_args.args[0]
                self.assertEqual(user.user_id, player.owner_user_id)
                self.assertTrue(player.is_owner)
                self.assertEqual("PICTURE", player.image_url)
                self.assertEqual("FIRST", player.first_name)
                self.assertEqual("MIDDLE LAST", player.last_name)
                self.assertEqual("EMAIL", player.email)

        # Test a saved user
        with patch.object(self.manager.firebase_client, "get_firebase_user", return_value={"user_id": "NEW_FB_ID", "name": "FIRST MIDDLE LAST", "email": "EMAIL", "picture": "PICTURE"}):
            with patch.object(self.manager.dao, "get_user_by_firebase_id", return_value=fixtures.user()):
                self.manager.validate_token("")
                self.assertIsNotNone(self.manager.user)
                self.assertEqual(fixtures.user(), self.manager.user)

    def test_get_players(self):
        self.assert_requires_auth(lambda: self.manager.get_players())

        with patch.object(self.manager.dao, "get_players", return_value=[fixtures.player()]):
            players = self.manager.get_players()
            self.assertEqual([fixtures.player()], players)

    def test_create_player(self):
        self.assert_requires_auth(lambda: self.manager.create_player(fixtures.player()))

        with patch.object(self.manager.dao, "create_player", return_value=fixtures.player()) as create_player_mock:
            player = self.manager.create_player(fixtures.player())
            self.assertEqual(fixtures.player(), player)

        create_player_mock.assert_called_once_with(fixtures.player())

    def test_update_player(self):
        self.assert_requires_auth(lambda: self.manager.update_player("", fixtures.player()))

        with patch.object(self.manager.dao, "get_player", return_value=None) as get_player_mock:
            with self.assertRaises(ServiceException) as e:
                self.manager.update_player("", fixtures.player())
            self.assertEqual(404, e.exception.status_code)
            get_player_mock.assert_called_once_with("")

        with patch.object(self.manager.dao, "get_player", return_value=fixtures.player()):
            with patch.object(self.manager.dao, "update_player", return_value=fixtures.player()) as update_player_mock:
                result = self.manager.update_player("", fixtures.player())
                self.assertEqual(fixtures.player(), result)
            update_player_mock.assert_called_once_with("", fixtures.player())

    def test_delete_player(self):
        self.assert_requires_auth(lambda: self.manager.delete_player(""))

        with patch.object(self.manager.dao, "get_player", return_value=None) as get_player_mock:
            with self.assertRaises(ServiceException) as e:
                self.manager.delete_player("")
            self.assertEqual(404, e.exception.status_code)
            get_player_mock.assert_called_once_with("")

        not_your_player = fixtures.player()
        not_your_player.owner_user_id = "not you"
        with patch.object(self.manager.dao, "get_player", return_value=not_your_player):
            with self.assertRaises(ServiceException) as e:
                self.manager.delete_player("")
            self.assertEqual(403, e.exception.status_code)

        you = fixtures.player()
        you.is_owner = True
        with patch.object(self.manager.dao, "get_player", return_value=you):
            with self.assertRaises(ServiceException) as e:
                self.manager.delete_player("")
            self.assertEqual(403, e.exception.status_code)

        your_player = fixtures.player()
        your_player.owner_user_id = self.manager.user.user_id
        with patch.object(self.manager.dao, "get_player", return_value=your_player):
            with patch.object(self.manager.dao, "delete_player") as delete_player_mock:
                result = self.manager.delete_player("")
                self.assertEqual({}, result)
            delete_player_mock.assert_called_once_with("")

    def test_get_matches(self):
        self.assert_requires_auth(lambda: self.manager.get_players())

        with patch.object(self.manager.dao, "get_matches", return_value=[fixtures.match()]):
            matches = self.manager.get_matches()
            self.assertEqual([fixtures.match()], matches)

    def test_create_match(self):
        self.assert_requires_auth(lambda: self.manager.create_match(fixtures.match()))

        with patch.object(self.manager.dao, "create_match", return_value=fixtures.match()) as create_match_mock:
            match = self.manager.create_match(fixtures.match())
            self.assertEqual(fixtures.match(), match)

        create_match_mock.assert_called_once_with(fixtures.match())

    def assert_requires_auth(self, fun: Callable):
        self.manager.user = None
        with self.assertRaises(ServiceException) as e:
            fun()
        self.assertEqual(401, e.exception.status_code)
        self.assertEqual("Unable to authenticate", e.exception.error_message)
        self.manager.user = fixtures.user()
