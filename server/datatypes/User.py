from dataclasses import dataclass

from utils.Serializable import Serializable


@dataclass
class User(Serializable):
    name: str
    password: str
