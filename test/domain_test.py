import unittest
from datetime import datetime

from domain.exceptions import DomainException
from domain.match import Match, GameScore, Stat
from domain.player import Player
from test import fixtures


class PlayerTest(unittest.TestCase):
    def test_from_dict_max_scenario(self):
        max_dict = get_player_dict()
        player = Player.from_dict(max_dict, fixtures.user())
        self.assertEqual("player_id", player.player_id)
        self.assertEqual(fixtures.user().user_id, player.owner_user_id)
        self.assertFalse(player.is_owner)
        self.assertEqual("first_name", player.first_name)
        self.assertEqual("last_name", player.last_name)
        self.assertEqual("image_url", player.image_url)
        self.assertEqual("LEFT", player.dominant_hand)
        self.assertEqual("notes", player.notes)
        self.assertEqual("phone_number", player.phone_number)
        self.assertEqual("email", player.email)
        self.assertEqual(4.5, player.level)

    def test_from_dict_min_scenario(self):
        min_dict = {
            "first_name": "first_name",
            "last_name": "last_name",
        }
        player = Player.from_dict(min_dict, fixtures.user())
        self.assertIsNotNone(player.player_id)
        self.assertIsNone(player.image_url)
        self.assertIsNone(player.dominant_hand)
        self.assertIsNone(player.notes)
        self.assertIsNone(player.phone_number)
        self.assertIsNone(player.email)
        self.assertIsNone(player.level)

    def test_from_dict_empty_id(self):
        no_id_dict = get_player_dict()
        no_id_dict["player_id"] = ""
        player = Player.from_dict(no_id_dict, fixtures.user())
        self.assertNotEqual("", player.player_id)

    def test_from_dict_missing_required_keys(self):
        def assert_error_without_key(key: str):
            tmp_dict = get_player_dict()
            tmp_dict.pop(key)
            with self.assertRaises(DomainException) as e:
                Player.from_dict(tmp_dict, fixtures.user())
            self.assertEqual(f"Missing required key '{key}' in request body", e.exception.error_message)

        assert_error_without_key("first_name")
        assert_error_without_key("last_name")


class MatchTest(unittest.TestCase):
    def test_from_dict_max_scenario(self):
        max_dict = get_match_dict()
        match = Match.from_dict(max_dict, fixtures.user())
        self.assertEqual("match_id", match.match_id)
        self.assertEqual(fixtures.user().user_id, match.user_id)
        self.assertEqual(2021, match.date.year)
        self.assertEqual(10, match.date.month)
        self.assertEqual(26, match.date.day)
        self.assertIsNotNone(match.team1_player1)
        self.assertIsNotNone(match.team1_player2)
        self.assertIsNotNone(match.team2_player1)
        self.assertIsNotNone(match.team2_player2)
        self.assertEqual(2, len(match.scores))
        self.assertEqual(3, len(match.stats))

    def test_from_dict_min_scenario(self):
        min_dict = {
            "date": "2021-10-26T18:35:12Z",
            "team1": [get_player_dict()],
            "team2": [get_player_dict()],
            "scores": [get_score_dict()],
        }
        match = Match.from_dict(min_dict, fixtures.user())
        self.assertIsNotNone(match.match_id)
        self.assertIsNone(match.team1_player2)
        self.assertIsNone(match.team2_player2)
        self.assertEqual(0, len(match.stats))

    def test_from_dict_empty_id(self):
        no_id_dict = get_match_dict()
        no_id_dict["match_id"] = ""
        match = Match.from_dict(no_id_dict, fixtures.user())
        self.assertNotEqual("", match.match_id)

    def test_from_dict_not_enough_players(self):
        with self.assertRaises(DomainException) as e:
            Match.from_dict({
                "date": "2021-10-26T18:35:12Z",
                "team1": [],
                "team2": [],
                "scores": [get_score_dict()],
                "stats": [],
            }, fixtures.user())
        self.assertEqual("Not enough players provided in each team", e.exception.error_message)

    def test_from_dict_no_scores(self):
        with self.assertRaises(DomainException) as e:
            Match.from_dict({
                "date": "2021-10-26T18:35:12Z",
                "team1": [get_player_dict()],
                "team2": [get_player_dict()],
                "scores": [],
                "stats": [],
            }, fixtures.user())
        self.assertEqual("No scores in the request body. A match must consist of at least one game", e.exception.error_message)

    def test_from_dict_missing_required_keys(self):
        def assert_error_without_key(key: str):
            tmp_dict = get_match_dict()
            tmp_dict.pop(key)
            with self.assertRaises(DomainException) as e:
                Match.from_dict(tmp_dict, fixtures.user())
            self.assertEqual(f"Missing required key '{key}' in request body", e.exception.error_message)

        assert_error_without_key("team1")
        assert_error_without_key("team2")
        assert_error_without_key("scores")

    def test_to_dict_max_scenario(self):
        d = fixtures.match().to_dict()
        self.assertEqual("match_id", d["match_id"])
        self.assertEqual(datetime(2020, 1, 1), d["date"])
        self.assertEqual(2, len(d["team1"]))
        self.assertEqual(2, len(d["team2"]))
        self.assertEqual(1, len(d["scores"]))
        self.assertEqual(1, len(d["stats"]))

    def test_to_dict_min_scenario(self):
        match = fixtures.match()
        match.team1_player2 = None
        match.team2_player2 = None
        d = match.to_dict()
        self.assertEqual(1, len(d["team1"]))
        self.assertEqual(1, len(d["team2"]))


class GameScoreTest(unittest.TestCase):
    def test_from_dict(self):
        score = GameScore.from_dict(get_score_dict())
        self.assertEqual(10, score.team1_score)
        self.assertEqual(0, score.team2_score)

    def test_from_dict_missing_required_keys(self):
        def assert_error_without_key(key: str):
            tmp_dict = get_score_dict()
            tmp_dict.pop(key)
            with self.assertRaises(DomainException) as e:
                GameScore.from_dict(tmp_dict)
            self.assertEqual(f"Missing required key '{key}' in request body", e.exception.error_message)

        assert_error_without_key("team1_score")
        assert_error_without_key("team2_score")


class StatTest(unittest.TestCase):
    def test_from_dict_max_scenario(self):
        stat = Stat.from_dict(get_stat_dict())
        self.assertEqual("match_id", stat.match_id)
        self.assertEqual("player_id", stat.player_id)
        self.assertEqual(0, stat.game_index)
        self.assertEqual("shot_result", stat.shot_result)
        self.assertEqual("shot_type", stat.shot_type)
        self.assertEqual("shot_side", stat.shot_side)

    def test_from_dict_min_scenario(self):
        d = get_stat_dict()
        d.pop("match_id")
        d.pop("shot_side")
        stat = Stat.from_dict(d)
        self.assertIsNone(stat.match_id)
        self.assertIsNone(stat.shot_side)

    def test_from_dict_missing_required_keys(self):
        def assert_error_without_key(key: str):
            tmp_dict = get_stat_dict()
            tmp_dict.pop(key)
            with self.assertRaises(DomainException) as e:
                Stat.from_dict(tmp_dict)
            self.assertEqual(f"Missing required key '{key}' in request body", e.exception.error_message)

        assert_error_without_key("player_id")
        assert_error_without_key("game_index")
        assert_error_without_key("shot_result")
        assert_error_without_key("shot_type")


def get_player_dict(): return {
    "player_id": "player_id",
    "first_name": "first_name",
    "last_name": "last_name",
    "image_url": "image_url",
    "dominant_hand": "LEFT",
    "notes": "notes",
    "phone_number": "phone_number",
    "email": "email",
    "level": 4.5,
}


def get_score_dict(): return {
    "team1_score": 10,
    "team2_score": 0,
}


def get_stat_dict(): return {
    "match_id": "match_id",
    "player_id": "player_id",
    "game_index": 0,
    "shot_result": "shot_result",
    "shot_type": "shot_type",
    "shot_side": "shot_side",
}


def get_match_dict(): return {
    "match_id": "match_id",
    "date": "2021-10-26T18:35:12Z",
    "team1": [
        get_player_dict(),
        get_player_dict(),
    ],
    "team2": [
        get_player_dict(),
        get_player_dict(),
    ],
    "scores": [
        get_score_dict(),
        get_score_dict(),
    ],
    "stats": [
        get_stat_dict(),
        get_stat_dict(),
        get_stat_dict(),
    ],
}


if __name__ == '__main__':
    unittest.main()
