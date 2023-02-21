from typing import List, Optional, Type, Union
from sqlalchemy.orm import Session
from app.core.security import get_password_hash

from app.db.seeder.base import BaseSeed
from app.models.user import User
from app.schemas.user import UserCreate
from app import crud


class UserSeed(BaseSeed[User, UserCreate]):
    def __init__(
        self,
        db: Session,
        data: Union[Type[UserCreate], List[Type[UserCreate]]],
        *args,
        **kwargs
    ) -> None:
        super(UserSeed, self).__init__(model=User, db=db, data=data, *args, **kwargs)

    def proceed(self, unifiere: str = "email") -> None:
        print(self.model.__name__)
        print(self.data)
        unifiere_obj: Optional[Type[self.model]] = None
        unifiere_obj_list: Optional[Type[self.model]] = None
        field = getattr(self.model, unifiere)
        equal = lambda f, a: f.__eq__(a)
        query = self.db.query().add_entity(self.model)

        if type(self.data) is not list:
            if unifiere != None:
                unifiere_obj = query.filter(equal(field, self.data[unifiere])).first()
            if not unifiere_obj and unifiere:
                hashed_password = get_password_hash(self.data["password"])
                del self.data.password
                user_in = User(**self.data, hashed_password=hashed_password)
                self.db.add(user_in)
                self.db.commit()
                self.db.refresh(user_in)
        else:
            for user in self.data:
                print(unifiere)
                if not unifiere == None:
                    unifiere_obj_list = query.filter(
                        equal(field, user[unifiere])
                    ).first()
                if (unifiere_obj_list == None and unifiere != None) or unifiere == None:
                    hashed_password = get_password_hash(user["password"])
                    del user["password"]
                    user_in = User(**user, hashed_password=hashed_password)
                    self.db.add(user_in)
                    self.db.commit()
                    self.db.refresh(user_in)
