import unittest
import json
import handler
from domain import *


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = MockManager()
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
        response = self.handler.handle(create_event("/players"))
        self.assertEqual(200, response["statusCode"])
        players = json.loads(response["body"])
        player = players[0]
        self.assertEqual("player_id", player["player_id"])
        self.assertEqual("owner_user_id", player["owner_user_id"])
        self.assertEqual("image_url", player["image_url"])
        self.assertEqual("first_name", player["first_name"])
        self.assertEqual("last_name", player["last_name"])
        self.assertEqual("dominant_hand", player["dominant_hand"])
        self.assertEqual("notes", player["notes"])
        self.assertEqual("phone_number", player["phone_number"])
        self.assertEqual("email", player["email"])
        self.assertEqual(5.0, player["level"])


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


# noinspection PyMethodMayBeStatic
class MockManager:
    def __init__(self):
        self.user = User("1", "fb1", "First", "Last", "hello.jpg")

    def validate_token(self, token):
        pass

    def get_players(self):
        return [Player("player_id", "owner_user_id", "image_url", "first_name", "last_name", "dominant_hand", "notes", "phone_number", "email", 5.0)]
