import os
import unittest
from datetime import datetime

from domain.exceptions import ServiceException
from domain.match import Match, GameScore, Stat
from domain.player import Player
from domain.user import User
from test import properties, fixtures
from da import DaoImpl


class Test(unittest.TestCase):
    dao: DaoImpl

    @classmethod
    def setUpClass(cls):
        os.environ["DB_HOST"] = properties.db_host
        os.environ["DB_USERNAME"] = properties.db_username
        os.environ["DB_PASSWORD"] = properties.db_password
        os.environ["DB_DATABASE_NAME"] = properties.db_database_name

        cls.dao = DaoImpl()

    def setUp(self) -> None:
        try:
            self.dao.execute("""insert into users (id, firebase_id, first_name, last_name, image_url) values 
                ('TEST1', 'fb1', 'Tester', 'One', 'test1.jpg'),
                ('TEST2', 'fb2', 'Tester', 'Two', 'test2.jpg'),
                ('TEST3', 'fb3', 'Tester', 'Three', 'test3.jpg'),
                ('TEST4', 'fb4', 'Tester', 'Four', 'test4.jpg')
            """)
            self.dao.execute("""insert into players (id, owner_user_id, is_owner, image_url, first_name, last_name, dominant_hand, notes, phone_number, email_address, level) values 
                ('player1', 'TEST1', True, 'p1.jpg', 'first', 'last', 'LEFT', 'notes', 'phone', 'email', 5.2),
                ('player2', 'TEST1', True, 'image.jpg', 'first', 'last', 'LEFT', 'notes', 'phone', 'email', 5.2),
                ('player3', 'TEST1', True, 'image.jpg', 'first', 'last', 'LEFT', 'notes', 'phone', 'email', 5.2),
                ('player4', 'TEST1', True, 'image.jpg', 'first', 'last', 'LEFT', 'notes', 'phone', 'email', 5.2)
            """)
            self.dao.execute("""insert into matches (id, user_id, date, team1_player1_id, team1_player2_id, team2_player1_id, team2_player2_id, scores) values 
                ('match1', 'TEST1', '2020-01-01 00:00:01', 'player1', null, 'player2', null, '10-1'),
                ('match2', 'TEST1', '2020-01-01 00:00:02', 'player1', 'player2', 'player3', 'player4', '10-1,2-10')
            """)
            self.dao.execute("""insert into stats (id, user_id, match_id, player_id, game_index, shot_result, shot_type, shot_side) values 
                ('stat1', 'TEST1', 'match1', 'player1', 0, 'WINNER', 'DROP', 'FOREHAND'),
                ('stat2', 'TEST1', 'match1', 'player1', 0, 'ERROR', 'SERVE', null)
            """)
        except:
            self.tearDown()
            exit()

    def tearDown(self) -> None:
        # These will cascade in order to delete the other ones
        self.dao.execute("delete from users where id in ('__TEST', 'TEST1', 'TEST2', 'TEST3', 'TEST4')")

    def test_get_user(self):
        # Test non-existent user
        user = self.dao.get_user("TEST0")
        self.assertIsNone(user)

        # Test regular user
        user = self.dao.get_user("TEST1")
        self.assertIsNotNone(user)
        self.assertEqual("TEST1", user.user_id)
        self.assertEqual("fb1", user.firebase_id)
        self.assertEqual("Tester", user.first_name)
        self.assertEqual("One", user.last_name)
        self.assertEqual("test1.jpg", user.image_url)

    def test_get_user_by_firebase_id(self):
        # Test non-existent user
        user = self.dao.get_user_by_firebase_id("fb0")
        self.assertIsNone(user)

        # Test regular user
        user = self.dao.get_user_by_firebase_id("fb1")
        self.assertIsNotNone(user)
        self.assertEqual("TEST1", user.user_id)

    def test_create_user(self):
        self.dao.create_user(User("__TEST", "fbid", "First", "Last", "test.jpg"))
        user: User = self.dao.get_one(User, "select id, firebase_id, first_name, last_name, image_url from users where ID = '__TEST'")
        self.assertIsNotNone(user)
        self.assertEqual("__TEST", user.user_id)
        self.assertEqual("fbid", user.firebase_id)
        self.assertEqual("First", user.first_name)
        self.assertEqual("Last", user.last_name)
        self.assertEqual("test.jpg", user.image_url)

    def test_get_players(self):
        players = self.dao.get_players("TEST0")
        self.assertEqual(0, len(players))

        players = self.dao.get_players("TEST1")
        self.assertEqual(4, len(players))

    def test_get_player(self):
        player = self.dao.get_player("player1")
        self.assertIsNotNone(player)

    def test_create_player(self):
        player = self.dao.create_player(Player("0", "TEST1", True, "image_url", "first_name", "last_name", "RIGHT", "notes", "phone_number", "email", 5.0))
        self.assertIsNotNone(player)
        self.assertEqual("0", player.player_id)
        self.assertEqual("TEST1", player.owner_user_id)
        self.assertIsInstance(player.is_owner, bool)
        self.assertTrue(player.is_owner)
        self.assertEqual("image_url", player.image_url)
        self.assertEqual("first_name", player.first_name)
        self.assertEqual("last_name", player.last_name)
        self.assertEqual("RIGHT", player.dominant_hand)
        self.assertEqual("notes", player.notes)
        self.assertEqual("phone_number", player.phone_number)
        self.assertEqual("email", player.email)
        self.assertEqual(5.0, player.level)

        # Create a player with everything as none
        player = self.dao.create_player(Player("-1", "TEST1", False, None, "first_name", "", None, None, None, None, None))
        self.assertIsNotNone(player)
        self.assertEqual("-1", player.player_id)
        self.assertEqual("TEST1", player.owner_user_id)
        self.assertIsInstance(player.is_owner, bool)
        self.assertFalse(player.is_owner)
        self.assertIsNone(player.image_url)
        self.assertEqual("first_name", player.first_name)
        self.assertEqual("", player.last_name)
        self.assertIsNone(player.dominant_hand)
        self.assertIsNone(player.notes)
        self.assertIsNone(player.phone_number)
        self.assertIsNone(player.email)
        self.assertIsNone(player.level)

    def test_update_player(self):
        player = self.dao.update_player("player1", Player("new_player_id", "new_owner_user_id", False, "new_image_url", "new_first", "new_last", "RIGHT", "new_notes", "new_phone", "new_email", 1.23))
        # You can't change the id or owner info
        self.assertEqual("player1", player.player_id)
        self.assertEqual("TEST1", player.owner_user_id)
        self.assertTrue(player.is_owner)
        # These can be changed
        self.assertEqual("new_image_url", player.image_url)
        self.assertEqual("new_first", player.first_name)
        self.assertEqual("new_last", player.last_name)
        self.assertEqual("RIGHT", player.dominant_hand)
        self.assertEqual("new_notes", player.notes)
        self.assertEqual("new_phone", player.phone_number)
        self.assertEqual("new_email", player.email)
        # This will get rounded by the db
        self.assertAlmostEqual(1.2, player.level)

    def test_delete_player(self):
        self.dao.delete_player("player1")
        self.assertIsNone(self.dao.get_player("player1"))

    def test_get_matches(self):
        matches = self.dao.get_matches("TEST1")
        self.assertEqual(2, len(matches))

        match = matches[0]
        self.assertEqual("player1", match.team1_player1.player_id)
        self.assertEqual("player2", match.team1_player2.player_id)
        self.assertEqual("player3", match.team2_player1.player_id)
        self.assertEqual("player4", match.team2_player2.player_id)
        self.assertEqual(2, len(match.scores))
        score = match.scores[0]
        self.assertEqual(10, score.team1_score)
        self.assertEqual(1, score.team2_score)
        score = match.scores[1]
        self.assertEqual(2, score.team1_score)
        self.assertEqual(10, score.team2_score)
        self.assertEqual(0, len(match.stats))

        match = matches[1]
        self.assertEqual("match1", match.match_id)
        self.assertEqual("TEST1", match.user_id)
        self.assertEqual(datetime(2020, 1, 1, 0, 0, 1), match.date)
        self.assertEqual("player1", match.team1_player1.player_id)
        self.assertIsNone(match.team1_player2)
        self.assertEqual("player2", match.team2_player1.player_id)
        self.assertIsNone(match.team2_player2)
        self.assertEqual(1, len(match.scores))
        score = match.scores[0]
        self.assertEqual(10, score.team1_score)
        self.assertEqual(1, score.team2_score)
        self.assertEqual(2, len(match.stats))
        stat = match.stats[0]
        self.assertEqual("player1", stat.player_id)
        self.assertEqual(0, stat.game_index)
        self.assertEqual("WINNER", stat.shot_result)
        self.assertEqual("DROP", stat.shot_type)
        self.assertEqual("FOREHAND", stat.shot_side)
        stat = match.stats[1]
        self.assertIsNone(stat.shot_side)

    def test_create_match(self):
        p1, p2, p3, p4 = fixtures.player(), fixtures.player(), fixtures.player(), fixtures.player()
        p1.player_id = "player1"
        p2.player_id = "player2"
        p3.player_id = "player3"
        p4.player_id = "player4"
        match = self.dao.create_match(Match(
            match_id="0",
            user_id="TEST1",
            date=datetime(2020, 1, 1, 2, 3, 4),
            team1_player1=p1,
            team1_player2=p2,
            team2_player1=p3,
            team2_player2=p4,
            scores=[GameScore(10, 4), GameScore(2, 0)],
            stats=[
                Stat(
                    match_id="",
                    player_id=p1.player_id,
                    game_index=0,
                    shot_result="ERROR",
                    shot_type="OVERHEAD",
                    shot_side="BACKHAND"
                ),
                Stat(
                    match_id="",
                    player_id=p2.player_id,
                    game_index=1,
                    shot_result="WINNER",
                    shot_type="SERVE",
                    shot_side=None
                )
            ]
        ))
        self.assertIsNotNone(match)
        self.assertEqual("0", match.match_id)
        self.assertEqual("TEST1", match.user_id)
        self.assertEqual(datetime(2020, 1, 1, 2, 3, 4), match.date)
        self.assertEqual("player1", match.team1_player1.player_id)
        # Player info should be fetched after creation
        self.assertEqual("p1.jpg", match.team1_player1.image_url)
        self.assertEqual("player2", match.team1_player2.player_id)
        self.assertEqual("player3", match.team2_player1.player_id)
        self.assertEqual("player4", match.team2_player2.player_id)
        self.assertEqual(2, len(match.scores))
        score = match.scores[0]
        self.assertEqual(10, score.team1_score)
        self.assertEqual(4, score.team2_score)
        score = match.scores[1]
        self.assertEqual(2, score.team1_score)
        self.assertEqual(0, score.team2_score)
        self.assertEqual(2, len(match.stats))
        stat = match.stats[0]
        self.assertEqual("0", stat.match_id)
        self.assertEqual("player1", stat.player_id)
        self.assertEqual(0, stat.game_index)
        self.assertEqual("ERROR", stat.shot_result)
        self.assertEqual("OVERHEAD", stat.shot_type)
        self.assertEqual("BACKHAND", stat.shot_side)
        stat = match.stats[1]
        self.assertEqual("0", stat.match_id)
        self.assertEqual("player2", stat.player_id)
        self.assertEqual(1, stat.game_index)
        self.assertEqual("WINNER", stat.shot_result)
        self.assertEqual("SERVE", stat.shot_type)
        self.assertIsNone(stat.shot_side)

        # Create a match with as little as possible
        match = self.dao.create_match(Match(
            match_id="-1",
            user_id="TEST1",
            date=datetime(2020, 1, 1, 2, 3, 4),
            team1_player1=p1,
            team1_player2=None,
            team2_player1=p2,
            team2_player2=None,
            scores=[GameScore(0, 1)],
            stats=[]
        ))
        self.assertIsNotNone(match)
        self.assertEqual("-1", match.match_id)
        self.assertEqual("player1", match.team1_player1.player_id)
        self.assertIsNone(match.team1_player2)
        self.assertEqual("player2", match.team2_player1.player_id)
        self.assertIsNone(match.team2_player2)
        self.assertEqual(1, len(match.scores))
        score = match.scores[0]
        self.assertEqual(0, score.team1_score)
        self.assertEqual(1, score.team2_score)
        self.assertEqual(0, len(match.stats))

        # If stats fail, everything rolls back
        with self.assertRaises(ServiceException):
            self.dao.create_match(Match(
                match_id="-2",
                user_id="TEST1",
                date=datetime(2020, 1, 1, 2, 3, 4),
                team1_player1=p1,
                team1_player2=p2,
                team2_player1=p3,
                team2_player2=p4,
                scores=[GameScore(10, 4), GameScore(2, 0)],
                stats=[
                    Stat(
                        match_id="",
                        player_id=p1.player_id,
                        game_index=0,
                        shot_result="ERROR",
                        shot_type="OVERHEAD",
                        shot_side="BACKHAND"
                    ),
                    Stat(
                        match_id="",
                        player_id="bad player",
                        game_index=1,
                        shot_result="WINNER",
                        shot_type="SERVE",
                        shot_side=None
                    )
                ]
            ))
        self.assertIsNone(self.dao.get_match("-2"))
