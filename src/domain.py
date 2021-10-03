import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

class Codable:
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        pass


@dataclass
class User(Codable):
    user_id: str
    firebase_id: str
    first_name: str
    last_name: str
    image_url: str


@dataclass
class Match(Codable):
    match_id: str
    user_id: str
    date: datetime
    team1_player1_id: str
    team1_player2_id: Optional[str]
    team2_player1_id: str
    team2_player2_id: Optional[str]
    scores: str


class DominantHand(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


@dataclass
class Player(Codable):
    player_id: str
    owner_user_id: str
    image_url: str
    first_name: str
    last_name: str
    dominant_hand: Optional[DominantHand] = None
    notes: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    level: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__
        d["dominant_hand"] = self.dominant_hand.name
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        try:
            player_id = d.get("player_id", "")
            if player_id == "":
                player_id = str(uuid.uuid4())

            dominant_hand = d.get("dominant_hand")
            if dominant_hand is not None:
                dominant_hand = DominantHand[dominant_hand]
            return Player(
                player_id,
                d["owner_user_id"],
                d["image_url"],
                d["first_name"],
                d["last_name"],
                dominant_hand,
                d.get("notes"),
                d.get("phone_number"),
                d.get("email"),
                d.get("level"),
            )
        except KeyError as e:
            raise DomainException(f"Missing required key '{e.args[0]}' in request body")


#### Non-DB Objects ####

class ServiceException(Exception, Codable):
    def __init__(self, message, status_code=500):
        self.error_message = message
        self.status_code = status_code


class DomainException(ServiceException):
    def __init__(self, message):
        super().__init__(message, 400)
