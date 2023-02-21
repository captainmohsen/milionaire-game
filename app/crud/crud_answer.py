from typing import Optional,List
from app.crud.base import CRUDBase
from app.models.answer import Answer
from app.schemas.answer import AnswerCreate, AnswerUpdate
from sqlalchemy.orm import Session
from pydantic.types import UUID4


class CRUDAnswer(CRUDBase[Answer, AnswerCreate, AnswerUpdate]):
    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Answer]:
        return db.query(Answer).offset(skip).limit(limit).all()

    def get_by_detail(self, db: Session, *, detail: str) -> Optional[Answer]:
        return db.query(self.model).filter(Answer.detail == detail).first()

    def get_by_question_id(self, db: Session, *, question_id: UUID4) -> Optional[Answer]:
        return db.query(self.model).filter(Answer.question_id == question_id).first()


answer = CRUDAnswer(Answer)