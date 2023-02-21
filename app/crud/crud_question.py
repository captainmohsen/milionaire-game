from typing import Optional,List
from app.crud.base import CRUDBase
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate
from sqlalchemy.orm import Session
from pydantic.types import UUID4


class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionUpdate]):

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Question]:
        return db.query(Question).offset(skip).limit(limit).all()

    def get_by_detail(self, db: Session, *, detail: str) -> Optional[Question]:
        return db.query(self.model).filter(Question.detail == detail).first()

    def get_by_id(self, db: Session, *, question_id: UUID4) -> Optional[Question]:
        return db.query(self.model).filter(Question.id == question_id).first()


question = CRUDQuestion(Question)