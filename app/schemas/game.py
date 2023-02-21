from datetime import datetime
from typing import Optional
from app.constants.enums import GameStatus

from pydantic import UUID4, BaseModel


# Shared properties
class GameBase(BaseModel):
    name: Optional[str]
    point: Optional[int]
    game_unique_number: Optional[int]
    status: Optional[GameStatus]
    user_id: Optional[UUID4]
    user_answer_id: Optional[str]


# Properties to receive via API on creation
class GameCreate(GameBase):
    user_id: Optional[UUID4]
    name: Optional[str]
    game_unique_number: Optional[int]


class PlayGame(BaseModel):
    name: Optional[str]
    game_unique_number: Optional[int]


class ShowGame(BaseModel):
    game_id: Optional[UUID4]
    question_id: Optional[UUID4]
    question_detail: Optional[str]
    currect_option: Optional[str]
    option1: Optional[str]
    option2: Optional[str]
    option3: Optional[str]


class SendAnswerGame(BaseModel):
    game_id: Optional[UUID4]
    question_id: Optional[UUID4]
    user_answer_detail: Optional[str]


class ShowResult(BaseModel):
    message: Optional[str]
    point: Optional[int]
    currect_option: Optional[str]


# Properties to receive via API on update
class GameUpdate(GameBase):
    pass


class GameInDBBase(GameBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class Game(GameInDBBase):
    pass


class GameInDB(GameInDBBase):
    pass
