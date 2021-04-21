from dataclasses import dataclass

from server.api.StatusCode import StatusCode
from utils.Serializable import Serializable


@dataclass
class Result(Serializable):
    status: StatusCode
