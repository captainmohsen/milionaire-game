import uuid
from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from app.db.base_class import Base


class Question(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    point = Column(Integer, nullable=True, default=0)
    detail = Column(String, nullable=False)
    correct_answer = Column(String, nullable=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("game.id"), primary_key=False)
    game = relationship("Game", back_populates="questions")
    answers = relationship('Answer', back_populates='question')

    @validates('point')
    def validate_username(self, key, point):
        if point < 5 or point > 25:
            raise AssertionError('point can not be smaller than 5 and bigger than 25')
