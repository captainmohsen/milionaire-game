from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel


# Shared properties
class AnswerBase(BaseModel):
    detail: Optional[str]
    question_id : Optional[UUID4]


# Properties to receive via API on creation
class AnswerCreate(AnswerBase):
    question_id : Optional[UUID4]
    detail: Optional[str]




# Properties to receive via API on update
class AnswerUpdate(AnswerBase):
    pass


class AnswerInDBBase(AnswerBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class Answer(AnswerInDBBase):
    pass


class AnswerInDB(AnswerInDBBase):
    pass