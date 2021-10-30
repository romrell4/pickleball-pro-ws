import itertools
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict

from pymysql.constants import FIELD_TYPE

from domain.exceptions import ServiceException
from domain.match import Match, GameScore, Stat
from domain.player import Player
from domain.user import User
import pymysql
import os


class Dao:
    def get_user(self, user_id: str) -> User: pass

    def get_user_by_firebase_id(self, firebase_id: str) -> Optional[User]: pass

    def create_user(self, user: User): pass

    def get_players(self, owner_user_id: str) -> List[Player]: pass

    def get_player(self, player_id: str) -> Player: pass

    def create_player(self, player: Player) -> Player: pass

    def update_player(self, player_id: str, player: Player) -> Player: pass

    def delete_player(self, player_id: str): pass

    def get_matches(self, user_id: str) -> List[Match]: pass

    def create_match(self, match: Match) -> Match: pass


class DaoImpl(Dao):
    def __init__(self):
        try:
            conv = pymysql.converters.conversions.copy()
            conv[FIELD_TYPE.DECIMAL] = float
            conv[FIELD_TYPE.NEWDECIMAL] = float
            conv[FIELD_TYPE.TINY] = lambda data: data == "1"
            self.conn = pymysql.connect(
                host=os.environ["DB_HOST"],
                user=(os.environ["DB_USERNAME"]),
                passwd=(os.environ["DB_PASSWORD"]),
                db=(os.environ["DB_DATABASE_NAME"]),
                conv=conv,
                autocommit=True
            )
        except Exception as e:
            print("ERROR: Could not connect to MySQL", e)
            raise ServiceException("Failed to connect to database")

    ### DB ACCESS FUNCTIONS ###

    def get_user(self, user_id: str) -> User:
        return self.get_one(User, "select id, firebase_id, first_name, last_name, image_url from users where id = %s", user_id)

    def get_user_by_firebase_id(self, firebase_id: str) -> Optional[User]:
        return self.get_one(User, "select id, firebase_id, first_name, last_name, image_url from users where firebase_id = %s", firebase_id)

    def create_user(self, user: User):
        self.execute("insert into users (id, firebase_id, first_name, last_name, image_url) values (%s, %s, %s, %s, %s)", user.user_id, user.firebase_id, user.first_name, user.last_name, user.image_url)

    def get_players(self, owner_user_id: str) -> List[Player]:
        return self.get_list(Player, "select id, owner_user_id, is_owner, image_url, first_name, last_name, dominant_hand, notes, phone_number, email_address, level from players where owner_user_id = %s", owner_user_id)

    def get_player(self, player_id: str) -> Optional[Player]:
        return self.get_one(Player, "select id, owner_user_id, is_owner, image_url, first_name, last_name, dominant_hand, notes, phone_number, email_address, level from players where id = %s", player_id)

    def create_player(self, player: Player) -> Player:
        self.execute("insert into players (id, owner_user_id, is_owner, image_url, first_name, last_name, dominant_hand, notes, phone_number, email_address, level) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                     player.player_id, player.owner_user_id, player.is_owner, player.image_url, player.first_name, player.last_name, player.dominant_hand, player.notes, player.phone_number, player.email, player.level)
        return self.get_player(player.player_id)

    def update_player(self, player_id: str, player: Player) -> Player:
        self.execute("update players set image_url = %s, first_name = %s, last_name = %s, dominant_hand = %s, notes = %s, phone_number = %s, email_address = %s, level = %s where id = %s",
                     player.image_url, player.first_name, player.last_name, player.dominant_hand, player.notes, player.phone_number, player.email, player.level, player_id)
        return self.get_player(player_id)

    def delete_player(self, player_id: str):
        self.execute("delete from players where id = %s", player_id)

    def get_matches(self, user_id: str) -> List[Match]:
        match_dtos = self.get_list(MatchDbDto, "select id, user_id, date, team1_player1_id, team1_player2_id, team2_player1_id, team2_player2_id, scores from matches where user_id = %s order by date desc", user_id)
        return self.to_matches(match_dtos)

    def create_match(self, match: Match) -> Match:
        self.conn.autocommit(False)
        try:
            self.execute("insert into matches (id, user_id, date, team1_player1_id, team1_player2_id, team2_player1_id, team2_player2_id, scores) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                         match.match_id, match.user_id, match.date, match.team1_player1.player_id, match.team1_player2.player_id if match.team1_player2 is not None else None, match.team2_player1.player_id, match.team2_player2.player_id if match.team2_player2 is not None else None, match.scores_db_str())
            if len(match.stats) > 0:
                stats_params = [[match.user_id, match.match_id, stat.player_id, stat.game_index, stat.shot_result, stat.shot_type, stat.shot_side] for stat in match.stats]
                self.execute_many("insert into stats (user_id, match_id, player_id, game_index, shot_result, shot_type, shot_side) values (%s, %s, %s, %s, %s, %s, %s)", *stats_params)
            self.conn.commit()
        except ServiceException as e:
            self.conn.rollback()
            raise e
        finally:
            self.conn.autocommit(True)
        return self.get_match(match.match_id)

    # Private functions

    def get_match(self, match_id: str) -> Optional[Match]:
        match_dto = self.get_one(MatchDbDto, "select id, user_id, date, team1_player1_id, team1_player2_id, team2_player1_id, team2_player2_id, scores from matches where id = %s", match_id)
        return self.to_matches([match_dto])[0] if match_dto is not None else None

    def get_stats(self, user_id: str) -> List[Stat]:
        return self.get_list(Stat, "select match_id, player_id, game_index, shot_result, shot_type, shot_side from stats where user_id = %s order by match_id, id", user_id)

    def to_matches(self, match_dtos: List) -> List[Match]:
        if len(match_dtos) == 0:
            return []

        user_id = match_dtos[0].user_id
        players = {k: list(v) for k, v in itertools.groupby(self.get_players(user_id), lambda player: player.player_id)}
        stats = {k: list(v) for k, v in itertools.groupby(self.get_stats(user_id), lambda stat: stat.match_id)}

        return [
            Match(
                match_id=dto.match_id,
                user_id=dto.user_id,
                date=dto.date,
                team1_player1=players[dto.team1_player1_id][0],
                team1_player2=players[dto.team1_player2_id][0] if dto.team1_player2_id is not None else None,
                team2_player1=players[dto.team2_player1_id][0],
                team2_player2=players[dto.team2_player2_id][0] if dto.team2_player2_id is not None else None,
                scores=[GameScore.from_db_str(game) for game in dto.scores.split(",")],
                stats=stats.get(dto.match_id, [])
            )
            for dto in match_dtos
        ]

    # UTILS

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

    def execute(self, sql, *args):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, args)
        except Exception as e:
            print(e)
            raise ServiceException("Error executing database command")

    def execute_many(self, sql, *args):
        try:
            with self.conn.cursor() as cur:
                cur.executemany(sql, args)
        except Exception as e:
            print(e)
            raise ServiceException("Error executing database command")


@dataclass
class MatchDbDto:
    match_id: str
    user_id: str
    date: datetime
    team1_player1_id: str
    team1_player2_id: str
    team2_player1_id: str
    team2_player2_id: str
    scores: str
