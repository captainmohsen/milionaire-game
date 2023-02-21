import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base




class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50))
    last_name = Column(String(50))
    fullname = column_property(first_name + " " + last_name)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    national_id = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    games = relationship('Game', back_populates='user')
    phone_verify = Column(Boolean(), default=False)
    user_role = relationship("UserRole", back_populates="user", uselist=False)

