import enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel



# Shared properties
class UserBase(BaseModel):
    phone_number: Optional[str]
    national_id: Optional[str]
    role: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    phone_number: Optional[str]
    national_id: Optional[str]
    fullname: Optional[str]
    first_name:Optional[str]
    is_complete: Optional[bool]
    father_name: Optional[str]
    role:Optional[str]




# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserResponse(UserInDBBase):
    pass

    class Config:
        orm_mode = True


class UserRegisterResponse(BaseModel):
    phone_number: str
