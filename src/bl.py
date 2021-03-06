import uuid
from datetime import datetime
from typing import List, Optional, Dict

from firebase_admin.auth import ExpiredIdTokenError, InvalidIdTokenError

from da import Dao
from domain.exceptions import ServiceException
from domain.match import Match, GameScore
from domain.player import Player
from domain.user import User
from firebase_client import FirebaseClient


class Manager:
    firebase_client = None
    user = None
    dao = None

    def validate_token(self, token: str) -> None: pass

    def get_players(self) -> List[Player]: pass

    def create_player(self, player: Player) -> Player: pass

    def update_player(self, player_id: str, player: Player) -> Player: pass

    def delete_player(self, player_id: str) -> Dict: pass

    def get_matches(self) -> List[Match]: pass

    def create_match(self, match: Match) -> Match: pass

    def delete_match(self, match_id: str) -> Dict: pass


class ManagerImpl(Manager):
    def __init__(self, firebase_client: FirebaseClient, dao: Dao):
        self.firebase_client = firebase_client
        self.dao = dao
        self.user = None

    def validate_token(self, token: Optional[str]):
        if token is None:
            return

        try:
            firebase_user = self.firebase_client.get_firebase_user(token)
            self.user = self.dao.get_user_by_firebase_id(firebase_user["user_id"])
            if self.user is None:
                try:
                    first_name, last_names = firebase_user["name"].split(" ", 1)
                except ValueError:
                    first_name, last_names = "", ""

                self.user = User(user_id=str(uuid.uuid4()), firebase_id=firebase_user["user_id"], first_name=first_name, last_name=last_names, image_url=firebase_user.get("picture"))
                self.dao.create_user(self.user)
                self.dao.create_player(
                    Player(
                        player_id=str(uuid.uuid4()),
                        owner_user_id=self.user.user_id,
                        is_owner=True,
                        image_url=self.user.image_url,
                        first_name=self.user.first_name,
                        last_name=self.user.last_name,
                        email=firebase_user.get("email")
                    )
                )
        except (KeyError, ValueError, InvalidIdTokenError, ExpiredIdTokenError) as e:
            print(e)
            self.user = None

    def get_players(self):
        self.require_auth()

        return self.dao.get_players(self.user.user_id)

    def create_player(self, player: Player) -> Player:
        self.require_auth()

        return self.dao.create_player(player)

    def update_player(self, player_id: str, player: Player) -> Player:
        self.require_auth()

        current_player = self.dao.get_player(player_id)
        if current_player is None:
            raise ServiceException("Player not found", 404)

        return self.dao.update_player(player_id, player)

    def delete_player(self, player_id: str) -> Dict:
        self.require_auth()

        player = self.dao.get_player(player_id)
        if player is None:
            raise ServiceException("Player not found.", 404)
        elif player.owner_user_id != self.user.user_id:
            raise ServiceException("You cannot delete a player you don't own.", 403)
        elif player.is_owner:
            raise ServiceException("You cannot delete yourself.", 403)

        self.dao.delete_player(player_id)
        return {}

    def get_matches(self) -> List[Match]:
        self.require_auth()

        return self.dao.get_matches(self.user.user_id)

    def create_match(self, match: Match) -> Match:
        self.require_auth()

        return self.dao.create_match(match)

    def delete_match(self, match_id: str) -> Dict:
        self.require_auth()

        match = self.dao.get_match(match_id)
        if match is None:
            raise ServiceException("Match not found.", 404)
        elif match.user_id != self.user.user_id:
            raise ServiceException("You cannot delete another player's matches.", 403)

        self.dao.delete_match(match_id)
        return {}

    def require_auth(self):
        if self.user is None:
            raise ServiceException("Unable to authenticate", 401)
