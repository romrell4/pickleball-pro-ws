import json
import unittest
from typing import Dict
from unittest.mock import patch

import handler
from bl import Manager
from domain.match import Match, GameScore, Stat
from domain.player import Player
from domain.user import User
from test import fixtures


class Test(unittest.TestCase):
    manager: Manager

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
        with patch.object(self.handler.manager, "get_players", return_value=[fixtures.player()]):
            response = self.handler.handle(create_event("/players"))
            self.assertEqual(200, response["statusCode"])
            self.assert_player_json(fixtures.player(), json.loads(response["body"])[0])

    def test_create_player(self):
        response = self.handler.handle(create_event("/players", method="POST", body="{}"))
        self.assertEqual(400, response["statusCode"])
        error = json.loads(response["body"])
        self.assertEqual("Missing required key 'first_name' in request body", error["error"])

        # Not having an owner_user_id should still pass
        input_player = fixtures.player()
        input_player_dict = input_player.to_dict()
        input_player_dict.pop("owner_user_id")
        with patch.object(self.handler.manager, "create_player", return_value=fixtures.player()) as create_player_mock:
            response = self.handler.handle(create_event("/players", method="POST", body=json.dumps(input_player_dict)))
            self.assertEqual(200, response["statusCode"])
            self.assert_player_json(fixtures.player(), json.loads(response["body"]))

        player = create_player_mock.call_args.args[0]
        self.assertIsInstance(player, Player)
        input_player.owner_user_id = self.manager.user.user_id
        input_player.is_owner = False
        self.assertEqual(input_player, player)

    def test_update_player(self):
        response = self.handler.handle(create_event("/players/{id}", method="PUT", path_params={"id": "ID"}, body="{}"))
        self.assertEqual(400, response["statusCode"])
        error = json.loads(response["body"])
        self.assertEqual("Missing required key 'first_name' in request body", error["error"])

        # Not having an owner_user_id should still pass
        input_player = fixtures.player()
        input_player_dict = input_player.to_dict()
        input_player_dict.pop("owner_user_id")
        with patch.object(self.handler.manager, "update_player", return_value=fixtures.player()) as update_player_mock:
            response = self.handler.handle(create_event("/players/{id}", method="PUT", path_params={"id": "ID"}, body=json.dumps(input_player_dict)))
            self.assertEqual(200, response["statusCode"])
            self.assert_player_json(fixtures.player(), json.loads(response["body"]))

        player_id, player = update_player_mock.call_args.args[0:2]
        self.assertEqual("ID", player_id)
        self.assertIsInstance(player, Player)
        input_player.owner_user_id = self.manager.user.user_id
        input_player.is_owner = False
        self.assertEqual(input_player, player)

    def test_delete_player(self):
        with patch.object(self.handler.manager, "delete_player", return_value={}) as delete_player_mock:
            response = self.handler.handle(create_event("/players/{id}", method="DELETE", path_params={"id": "ID"}))
            self.assertEqual(200, response["statusCode"])
            self.assertEqual({}, json.loads(response["body"]))

        player_id = delete_player_mock.call_args.args[0]
        self.assertEqual("ID", player_id)

    def test_get_matches(self):
        with patch.object(self.handler.manager, "get_matches", return_value=[fixtures.match()]):
            response = self.handler.handle(create_event("/matches"))
            self.assertEqual(200, response["statusCode"])
            self.assert_match_json(fixtures.match(), json.loads(response["body"])[0])

    def test_create_match(self):
        # TODO
        pass

    def test_delete_match(self):
        # TODO
        pass

    def assert_player_json(self, expected_player: Player, json_player: Dict):
        self.assertEqual(expected_player.player_id, json_player["player_id"])
        self.assertEqual(expected_player.owner_user_id, json_player["owner_user_id"])
        self.assertEqual(expected_player.is_owner, json_player["is_owner"])
        self.assertEqual(expected_player.image_url, json_player["image_url"])
        self.assertEqual(expected_player.first_name, json_player["first_name"])
        self.assertEqual(expected_player.last_name, json_player["last_name"])
        self.assertEqual(expected_player.dominant_hand, json_player["dominant_hand"])
        self.assertEqual(expected_player.notes, json_player["notes"])
        self.assertEqual(expected_player.phone_number, json_player["phone_number"])
        self.assertEqual(expected_player.email, json_player["email"])
        self.assertEqual(expected_player.level, json_player["level"])

    def assert_match_json(self, expected_match: Match, json_match: Dict):
        self.assertEqual(expected_match.match_id, json_match["match_id"])
        self.assertTrue(json_match["date"].endswith("Z"))
        self.assert_player_json(expected_match.team1_player1, json_match["team1"][0])
        self.assert_player_json(expected_match.team1_player2, json_match["team1"][1] if len(json_match["team1"]) > 1 else None)
        self.assert_player_json(expected_match.team2_player1, json_match["team2"][0])
        self.assert_player_json(expected_match.team2_player2, json_match["team2"][1] if len(json_match["team2"]) > 1 else None)
        for expected_score, json_score in zip(expected_match.scores, json_match["scores"]):
            self.assert_score_json(expected_score, json_score)
        for expected_stat, json_stat in zip(expected_match.stats, json_match["stats"]):
            self.assert_stat_json(expected_stat, json_stat)

    def assert_score_json(self, expected_score: GameScore, json_score: Dict):
        self.assertEqual(expected_score.team1_score, json_score["team1_score"])
        self.assertEqual(expected_score.team2_score, json_score["team2_score"])

    def assert_stat_json(self, expected_stat: Stat, json_stat: Dict):
        self.assertEqual(expected_stat.player_id, json_stat["player_id"])
        self.assertEqual(expected_stat.game_index, json_stat["game_index"])
        self.assertEqual(expected_stat.shot_result, json_stat["shot_result"])
        self.assertEqual(expected_stat.shot_type, json_stat["shot_type"])
        self.assertEqual(expected_stat.shot_side, json_stat["shot_side"])


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
