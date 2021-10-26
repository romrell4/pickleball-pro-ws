import uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any

from domain.base import DomainBase
from domain.exceptions import DomainException
from domain.user import User


@dataclass
class Player(DomainBase):
    player_id: str
    owner_user_id: str
    is_owner: bool
    image_url: Optional[str]
    first_name: str
    last_name: str
    dominant_hand: Optional[str] = None
    notes: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    level: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any], user: User):
        try:
            player_id = d.get("player_id", "")
            if player_id == "":
                player_id = str(uuid.uuid4())

            return Player(
                player_id=player_id,
                owner_user_id=user.user_id,
                is_owner=False,
                image_url=d.get("image_url"),
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
