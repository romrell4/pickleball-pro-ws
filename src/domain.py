from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_id: str
    firebase_id: str
    first_name: str
    last_name: str
    image_url: str


@dataclass
class Match:
    match_id: str
    user_id: str
    date: datetime
    team1_player1_id: str
    team1_player2_id: Optional[str]
    team2_player1_id: str
    team2_player2_id: Optional[str]
    scores: str


@dataclass
class Player:
    player_id: str
    owner_user_id: str
    image_url: str
    first_name: str
    last_name: str
    dominant_hand: str
    notes: str
    phone_number: str
    email: str
    level: float


#### Non-DB Objects ####

class ServiceException(Exception):
    def __init__(self, message, status_code=500):
        self.error_message = message
        self.status_code = status_code


class DomainException(ServiceException):
    def __init__(self, message):
        super().__init__(message, 400)
