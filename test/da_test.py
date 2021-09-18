import os
import unittest

from test import properties
from da import Dao
from domain import *


class Test(unittest.TestCase):
    dao: Dao

    @classmethod
    def setUpClass(cls):
        os.environ["DB_HOST"] = properties.db_host
        os.environ["DB_USERNAME"] = properties.db_username
        os.environ["DB_PASSWORD"] = properties.db_password
        os.environ["DB_DATABASE_NAME"] = properties.db_database_name

        cls.dao = Dao()

    def setUp(self) -> None:
        try:
            self.dao.insert("""INSERT INTO users (id, firebase_id, first_name, last_name, image_url) VALUES 
                ('TEST1', 'fb1', 'Tester', 'One', 'test1.jpg'),
                ('TEST2', 'fb2', 'Tester', 'Two', 'test2.jpg'),
                ('TEST3', 'fb3', 'Tester', 'Three', 'test3.jpg'),
                ('TEST4', 'fb4', 'Tester', 'Four', 'test4.jpg')
            """)
        except:
            self.tearDown()
            exit()

    def tearDown(self) -> None:
        # These will cascade in order to delete the other ones
        self.dao.execute("DELETE FROM users where id in ('__TEST', 'TEST1', 'TEST2', 'TEST3', 'TEST4')")

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
        user: User = self.dao.get_one(User, "SELECT id, firebase_id, first_name, last_name, image_url FROM users where ID = '__TEST'")
        self.assertIsNotNone(user)
        self.assertEqual("__TEST", user.user_id)
        self.assertEqual("fbid", user.firebase_id)
        self.assertEqual("First", user.first_name)
        self.assertEqual("Last", user.last_name)
        self.assertEqual("test.jpg", user.image_url)
