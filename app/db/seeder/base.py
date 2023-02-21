from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar, Union

from app.db.base_class import Base
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class BaseSeed(ABC, Generic[ModelType, CreateSchemaType]):
    def __init__(
        self,
        *,
        db: Session,
        data: Optional[Union[Type[CreateSchemaType], List[Type[CreateSchemaType]]]],
        model: Type[ModelType]
    ) -> None:
        self.db = db
        self.data = data
        self.model = model

    def proceed(self, unifiere: Optional[str]) -> None:
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
                model_obj_in = self.model(**self.data)
                self.db.add(model_obj_in)
                self.db.commit()
                self.db.refresh(model_obj_in)
        else:
            for data in self.data:
                if not unifiere == None:
                    unifiere_obj_list = query.filter(
                        equal(field, data[unifiere])
                    ).first()
                if (unifiere_obj_list == None and unifiere != None) or unifiere == None:
                    model_obj_in = self.model(**data)
                    self.db.add(model_obj_in)
                    self.db.commit()
                    self.db.refresh(model_obj_in)
                    unifiere_obj_list: Optional[Type[self.model]] = None
