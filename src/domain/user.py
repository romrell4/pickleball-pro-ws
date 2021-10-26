from dataclasses import dataclass

from domain.base import DomainBase


@dataclass
class User(DomainBase):
    user_id: str
    firebase_id: str
    first_name: str
    last_name: str
    image_url: str
