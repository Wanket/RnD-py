from enum import Enum


class StatusCode(Enum):
    Success = 0

    UserAlreadyExist = 1
    InvalidUsernameOrPassword = 2
