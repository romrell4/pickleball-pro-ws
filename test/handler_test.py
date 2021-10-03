import unittest
import json
from unittest.mock import patch

import handler
from bl import Manager
from domain import *


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = Manager()
        cls.manager.user = User("1", "fb1", "First", "Last", "hello.jpg")
        cls.handler = handler.Handler(cls.manager)

    def test_login_user(self):
        response = self.handler.handle(create_event("/users", method="POST"))
        self.assertEqual(200, response["statusCode"])
        user = json.loads(response["body"])
        self.assertEqual("1", user["user_id"])
        self.assertEqual("fb1", user["firebase_id"])
        self.assertEqual("First", user["first_name"])
        self.assertEqual("Last", user["last_name"])
        self.assertEqual("hello.jpg", user["image_url"])

    def test_get_players(self):
        with patch.object(self.handler.manager, "get_players", return_value=[Player("player_id", "owner_user_id", "image_url", "first_name", "last_name", DominantHand.LEFT, "notes", "phone_number", "email", 5.0)]):
            response = self.handler.handle(create_event("/players"))
            self.assertEqual(200, response["statusCode"])
            players = json.loads(response["body"])
            player = players[0]
            self.assertEqual("player_id", player["player_id"])
            self.assertEqual("owner_user_id", player["owner_user_id"])
            self.assertEqual("image_url", player["image_url"])
            self.assertEqual("first_name", player["first_name"])
            self.assertEqual("last_name", player["last_name"])
            self.assertEqual("LEFT", player["dominant_hand"])
            self.assertEqual("notes", player["notes"])
            self.assertEqual("phone_number", player["phone_number"])
            self.assertEqual("email", player["email"])
            self.assertEqual(5.0, player["level"])

    def test_create_player(self):
        response = self.handler.handle(create_event("/players", method="POST", body="{}"))
        self.assertEqual(400, response["statusCode"])
        error = json.loads(response["body"])
        self.assertEqual("Missing required key 'owner_user_id' in request body", error["error"])

        with patch.object(self.handler.manager, "create_player", return_value=Player("player_id", "owner_user_id", "image_url", "first_name", "last_name", DominantHand.RIGHT, "notes", "phone_number", "email", 5.0)) as create_player:
            response = self.handler.handle(create_event("/players", method="POST", body=json.dumps(Player("", "owner", "image", "first", "last", DominantHand.RIGHT).__dict__)))
            self.assertEqual(200, response["statusCode"])
            player = json.loads(response["body"])
            self.assertEqual("player_id", player["player_id"])
            self.assertEqual("owner_user_id", player["owner_user_id"])
            self.assertEqual("image_url", player["image_url"])
            self.assertEqual("first_name", player["first_name"])
            self.assertEqual("last_name", player["last_name"])
            self.assertEqual("RIGHT", player["dominant_hand"])
            self.assertEqual("notes", player["notes"])
            self.assertEqual("phone_number", player["phone_number"])
            self.assertEqual("email", player["email"])
            self.assertEqual(5.0, player["level"])

        player = create_player.call_args.args[0]
        self.assertIsInstance(player, Player)
        self.assertIsNotNone(player.player_id)
        self.assertIsNot("", player.player_id)


def create_event(resource, path_params=None, method="GET", body=None, query_params=None):
    event = {
        "resource": resource,
        "httpMethod": method,
        "headers": {"X-Firebase-Token": ""}
    }
    if path_params is not None:
        event["pathParameters"] = path_params
    if body is not None:
        event["body"] = body
    if query_params is not None:
        event["queryStringParameters"] = query_params
    return event
