from datetime import datetime

from domain.match import Match, GameScore, Stat
from domain.player import Player
from domain.user import User


def user(): return User(
    user_id="USER1",
    firebase_id="FB_ID",
    first_name="User",
    last_name="One",
    image_url="user.jpg"
)


def player(): return Player(
    player_id="player_id",
    owner_user_id="owner_user_id",
    is_owner=False,
    image_url="image_url",
    first_name="first_name",
    last_name="last_name",
    dominant_hand="RIGHT",
    notes="notes",
    phone_number="phone_number",
    email="email",
    level=5.0
)


def score(): return GameScore(team1_score=1, team2_score=2)


def stat(): return Stat(
    match_id="match_id",
    player_id="player_id",
    game_index=0,
    shot_result="WINNER",
    shot_type="DROP",
    shot_side="FOREHAND",
)


def match(): return Match(
    match_id="match_id",
    user_id="user_id",
    date=datetime(2020, 1, 1),
    team1_player1=player(),
    team1_player2=player(),
    team2_player1=player(),
    team2_player2=player(),
    scores=[score()],
    stats=[stat()],
)
