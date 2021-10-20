import os
import unittest

from test import properties, fixtures
from da import DaoImpl
from domain import *


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
            self.dao.insert("""insert into users (id, firebase_id, first_name, last_name, image_url) values 
                ('TEST1', 'fb1', 'Tester', 'One', 'test1.jpg'),
                ('TEST2', 'fb2', 'Tester', 'Two', 'test2.jpg'),
                ('TEST3', 'fb3', 'Tester', 'Three', 'test3.jpg'),
                ('TEST4', 'fb4', 'Tester', 'Four', 'test4.jpg')
            """)
            self.dao.insert("""insert into players (id, owner_user_id, image_url, first_name, last_name, dominant_hand, notes, phone_number, email_address, level) values 
                ('1', 'TEST1', 'image.jpg', 'first', 'last', 'LEFT', 'notes', 'phone', 'email', 5.2)
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
        self.assertEqual(1, len(players))

    def test_get_player(self):
        player = self.dao.get_player("1")
        self.assertIsNotNone(player)

    def test_create_player(self):
        player = self.dao.create_player(Player("0", "TEST1", "image_url", "first_name", "last_name", "RIGHT", "notes", "phone_number", "email", 5.0))
        self.assertIsNotNone(player)
        self.assertEqual("0", player.player_id)
        self.assertEqual("TEST1", player.owner_user_id)
        self.assertEqual("image_url", player.image_url)
        self.assertEqual("first_name", player.first_name)
        self.assertEqual("last_name", player.last_name)
        self.assertEqual("RIGHT", player.dominant_hand)
        self.assertEqual("notes", player.notes)
        self.assertEqual("phone_number", player.phone_number)
        self.assertEqual("email", player.email)
        self.assertEqual(5.0, player.level)

        # Create a player with everything as none
        player = self.dao.create_player(Player("-1", "TEST1", "image_url", "first_name", "", None, None, None, None, None))
        self.assertIsNotNone(player)
        self.assertEqual("-1", player.player_id)
        self.assertEqual("TEST1", player.owner_user_id)
        self.assertEqual("image_url", player.image_url)
        self.assertEqual("first_name", player.first_name)
        self.assertEqual("", player.last_name)
        self.assertIsNone(player.dominant_hand)
        self.assertIsNone(player.notes)
        self.assertIsNone(player.phone_number)
        self.assertIsNone(player.email)
        self.assertIsNone(player.level)

    def test_update_player(self):
        player = self.dao.update_player("1", Player("new_player_id", "new_owner_user_id", "new_image_url", "new_first", "new_last", "RIGHT", "new_notes", "new_phone", "new_email", 1.23))
        # You can't change the id or owner id
        self.assertEqual("1", player.player_id)
        self.assertEqual("TEST1", player.owner_user_id)
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
        self.dao.delete_player("1")
        self.assertIsNone(self.dao.get_player("1"))
