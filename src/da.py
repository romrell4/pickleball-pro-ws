from typing import List

from domain import *
import pymysql
import os


class Dao:
    def __init__(self):
        try:
            self.conn = pymysql.connect(host=os.environ["DB_HOST"], user=(os.environ["DB_USERNAME"]), passwd=(os.environ["DB_PASSWORD"]), db=(os.environ["DB_DATABASE_NAME"]), autocommit=True)
        except Exception as e:
            print("ERROR: Could not connect to MySQL", e)
            raise ServiceException("Failed to connect to database")

    ### DB ACCESS FUNCTIONS ###

    def get_user(self, user_id: str) -> User:
        return self.get_one(User, "select id, firebase_id, first_name, last_name, image_url from users where id = %s", user_id)

    def get_user_by_firebase_id(self, firebase_id: str) -> Optional[User]:
        return self.get_one(User, "select id, firebase_id, first_name, last_name, image_url from users where firebase_id = %s", firebase_id)

    def create_user(self, user: User):
        self.insert("insert into users (id, firebase_id, first_name, last_name, image_url) values (%s, %s, %s, %s, %s)", user.user_id, user.firebase_id, user.first_name, user.last_name, user.image_url)

    def get_players(self, owner_user_id: str) -> List[Player]:
        return self.get_list(Player, "select id, owner_user_id, image_url, first_name, last_name, dominant_hand, notes, phone_number, email_address, level from players where owner_user_id = %s", owner_user_id)

    ### UTILS ###

    def get_list(self, klass, sql, *args):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, args)
                results = []
                for row in cur.fetchall():
                    results.append(klass(*row))
                return results
        except Exception as e:
            print(e)
            raise ServiceException("Error getting data from database")

    def get_one(self, klass, sql, *args):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, args)
                row = cur.fetchone()
                if row is not None:
                    return klass(*row)
                return None
        except Exception as e:
            print(e)
            raise ServiceException("Error getting data from database")

    def insert(self, sql, *args):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, args)
                return cur.lastrowid
        except Exception as e:
            print(e)
            raise ServiceException("Error inserting data into database")

    def execute(self, sql, *args):
        try:
            with self.conn.cursor() as cur:
                affected_rows = cur.execute(sql, args)
                print(sql, args, affected_rows)
        except Exception as e:
            print(e)
            raise ServiceException("Error executing database command")
