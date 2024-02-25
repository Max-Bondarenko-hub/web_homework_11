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
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    name: str
    surname: Optional[str]
    email: EmailStr
    phone: str
    birthdate: date
    additional_data: Optional[str]

    class Config:
        from_attributes = True


class UserUpdate(UserModel): ...


class UserNameQuery(BaseModel):
    user_name: str


class AccountModel(BaseModel):
    login: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=6, max_length=15)


class AccountDb(BaseModel):
    id: int
    login: str
    email: str
    avatar: str

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    login: AccountDb
    detail: str = "Account successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
