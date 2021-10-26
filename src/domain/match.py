import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

from domain.base import DomainBase
from domain.exceptions import DomainException
from domain.player import Player
from domain.user import User


@dataclass
class GameScore(DomainBase):
    team1_score: int
    team2_score: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any], user: User):
        try:
            return GameScore(d["team1_score"], d["team2_score"])
        except KeyError as e:
            raise DomainException(f"Missing required key '{e.args[0]}' in request body")


@dataclass
class Stat(DomainBase):
    player_id: str
    game_index: int
    shot_result: str
    shot_type: str
    shot_side: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any], user: User):
        try:
            return Stat(d["player_id"], d["game_index"], d["shot_result"], d["shot_type"], d.get("shot_side"))
        except KeyError as e:
            raise DomainException(f"Missing required key '{e.args[0]}' in request body")


@dataclass
class Match(DomainBase):
    match_id: str
    user_id: str
    date: datetime
    team1_player1: Player
    team1_player2: Optional[Player]
    team2_player1: Player
    team2_player2: Optional[Player]
    scores: List[GameScore]
    stats: List[Stat]

    @classmethod
    def from_dict(cls, d: Dict[str, Any], user: User):
        try:
            match_id = d.get("match_id", "")
            if match_id == "":
                match_id = str(uuid.uuid4())

            team1, team2 = d["team1"], d["team2"]
            if len(team1) == 0 or len(team2) == 0:
                raise DomainException("Not enough players provided in each team")

            scores = [GameScore.from_dict(score, user) for score in d["scores"]]
            if len(scores) == 0:
                raise DomainException("No scores in the request body. A match must consist of at least one game")
            stats = [Stat.from_dict(stat, user) for stat in d.get("stats", [])]

            return Match(
                match_id=match_id,
                user_id=user.user_id,
                date=datetime.strptime(d["date"], "%Y-%m-%dT%H:%M:%S%z"),
                team1_player1=Player.from_dict(team1[0], user=user),
                team1_player2=Player.from_dict(team1[1], user=user) if len(team1) > 1 else None,
                team2_player1=Player.from_dict(team2[0], user=user),
                team2_player2=Player.from_dict(team2[1], user=user) if len(team2) > 1 else None,
                scores=scores,
                stats=stats
            )
        except KeyError as e:
            raise DomainException(f"Missing required key '{e.args[0]}' in request body")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "date": self.date,
            "team1": [player.to_dict() for player in [self.team1_player1, self.team1_player2] if player is not None],
            "team2": [player.to_dict() for player in [self.team2_player1, self.team2_player2] if player is not None],
            "scores": [score.to_dict() for score in self.scores],
            "stats": [stat.to_dict() for stat in self.stats],
        }
