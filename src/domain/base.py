from typing import Dict, Any

class DomainBase:
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls, d: Dict[str, Any], user):
        pass

    @classmethod
    def from_db(cls, *args):
        return cls.__init__(args)
