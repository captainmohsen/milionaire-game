import json
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone_number == phone).first()

    def get_by_id(
            self, db: Session, *, safir_id: str
    ) -> Optional[User]:
        return db.query(User).filter(User.id == safir_id).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:

        try:
            db_obj = User(
                phone_number=obj_in.phone_number,
                national_id=obj_in.national_id,
                is_active=True,
                hashed_password=get_password_hash(obj_in.password),
            )
           

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except Exception as e:
            print("crud", e)
            raise HTTPException(
                status_code=500,
                detail=json.dumps(
                    {
                        "message": "The user with this username already exists in the system",
                        "error": e,
                    }
                ),
            )

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, phone: str, password: str) -> Optional[User]:
        user = self.get_by_phone(db, phone=phone)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def phone_verify(self, user: User) -> bool:
        return user.phone_verify



user = CRUDUser(User)
