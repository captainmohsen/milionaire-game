from datetime import datetime
from typing import Optional
from unittest import result
from humps import camelize, is_camelcase
from pydantic import UUID4, BaseModel


def camel_case(s: str) -> str:
    if is_camelcase(s):
        return s
    return camelize(s)


class BaseSchemaModel(BaseModel):
    class Config:
        alias_generator = camel_case
        allow_population_by_field_name = True


class DatabaseRequirementField(BaseSchemaModel): 
    id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class DeleteResponse(BaseSchemaModel):
    result: bool