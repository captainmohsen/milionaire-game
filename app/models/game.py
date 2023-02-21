import uuid
from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.constants.enums import GameStatus


class Game(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    point = Column(Integer, nullable=True, default=0)
    name = Column(String, nullable=True)
    status = Column(Enum(GameStatus), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=False)
    user = relationship("User", back_populates="games")
    questions = relationship('Question', back_populates='game')
    user_answer_id = Column(String, nullable=True)
    game_unique_number = Column(Numeric, nullable=True)
