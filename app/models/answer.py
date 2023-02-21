import uuid
from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Answer(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detail = Column(String, nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("question.id"), primary_key=False)
    question = relationship("Question", back_populates="answers")
