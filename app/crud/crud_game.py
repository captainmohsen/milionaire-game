from typing import Optional, List
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate
from sqlalchemy.orm import Session
from pydantic.types import UUID4


class CRUDGame(CRUDBase[Game, GameCreate, GameUpdate]):

    def create(self, db: Session, *, obj_in: GameCreate, user_id: str, unique_number: str) -> Game:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, status="STARTED", user_id=user_id, game_unique_number=unique_number
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100, user_id: str
    ) -> List[Game]:
        return db.query(Game).filter(Game.user_id == user_id).offset(skip).limit(limit).all()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Game]:
        return db.query(self.model).filter(Game.name == name).first()

    def get_by_id(self, db: Session, *, game_id: UUID4) -> Optional[Game]:
        return db.query(self.model).filter(Game.id == game_id).first()

    def get_by_unique_number(self, db: Session, *, unique_number: int) -> Optional[Game]:
        return db.query(self.model).filter(Game.game_unique_number == unique_number).all()


game = CRUDGame(Game)
