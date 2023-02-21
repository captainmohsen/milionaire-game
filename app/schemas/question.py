from datetime import datetime
from typing import Optional
from app.constants.enums import GameStatus

from pydantic import UUID4, BaseModel


# Shared properties
class QuestionBase(BaseModel):
    detail: Optional[str]
    correct_answer: Optional[str]
    point: Optional[int]
    game_id: Optional[UUID4]


# Properties to receive via API on creation
class QuestionCreate(QuestionBase):
    game_id: Optional[UUID4]
    detail: Optional[str]
    correct_answer: Optional[str]


# Properties to receive via API on update
class QuestionUpdate(QuestionBase):
    pass


class QuestionInDBBase(QuestionBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class Question(QuestionInDBBase):
    pass


class QuestionInDB(QuestionInDBBase):
    pass
