import json
from typing import TypeVar, Type


class Serializable:
    def serialize(self) -> str:
        return json.dumps(self.__dict__, default=lambda o: o.__dict__)

    T = TypeVar("T")

    @staticmethod
    def deserialize(t: Type[T], data: str) -> T:
        return t(**json.loads(data))
