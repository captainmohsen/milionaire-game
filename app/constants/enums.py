from enum import Enum


class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DEACTIVE = "DEACTIVE"

class GameStatus(str, Enum):
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"