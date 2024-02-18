from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserModel(BaseModel):
    name: str = Field(max_length=50)
    surname: str = Field(None, max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthdate: date
    additional_data: str = None

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    name: str
    surname: Optional[str]
    email: EmailStr
    phone: str
    birthdate: date
    additional_data: Optional[str]

    class Config:
        orm_mode = True


class UserUpdate(UserModel):
    ...


class UserNameQuery(BaseModel):
    user_name: str
