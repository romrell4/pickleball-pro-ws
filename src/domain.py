import uuid
from dataclasses import dataclass
from datetime import datetime
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

    # TODO: Determine how to break down the scores into domain objects...

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        # TODO: Read from nested structure
        super().from_dict(d)

    def to_dict(self) -> Dict[str, Any]:
        # TODO: Turn into nested structure
        return super().to_dict()


@dataclass
class Player(Codable):
    player_id: str
    owner_user_id: str
    image_url: str
    first_name: str
    last_name: str
    dominant_hand: Optional[str] = None
    notes: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    level: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        try:
            player_id = d.get("player_id", "")
            if player_id == "":
                player_id = str(uuid.uuid4())

            print(d.get("level"))

            return Player(
                player_id=player_id,
                # The owner id won't be passed by the FE. It will be filled in before being saved
                owner_user_id="",
                image_url=d["image_url"],
                first_name=d["first_name"],
                last_name=d["last_name"],
                dominant_hand=d.get("dominant_hand"),
                notes=d.get("notes"),
                phone_number=d.get("phone_number"),
                email=d.get("email"),
                level=d.get("level"),
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
