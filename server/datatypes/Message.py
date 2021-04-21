from dataclasses import dataclass

from utils.Serializable import Serializable


@dataclass
class Message(Serializable):
    datetime: int
    author: str
    text: str


@dataclass
class MessageToSend(Serializable):
    text: str
