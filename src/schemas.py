from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserModel(BaseModel):
    """
    Represents a model for user data.

    :param name: The user's first name.
    :type name: str
    :param surname: The user's last name.
    :type surname: str, optional
    :param email: The user's email address.
    :type email: EmailStr
    :param phone: The user's phone number.
    :type phone: str
    :param birthdate: The user's date of birth.
    :type birthdate: date
    :param additional_data: Additional data about the user.
    :type additional_data: str, optional
    """
    name: str = Field(max_length=50)
    surname: str = Field(None, max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthdate: date
    additional_data: str = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Represents a model for user response data.

    :param id: The user's ID.
    :type id: int
    :param name: The user's first name.
    :type name: str
    :param surname: The user's last name.
    :type surname: str, optional
    :param email: The user's email address.
    :type email: EmailStr
    :param phone: The user's phone number.
    :type phone: str
    :param birthdate: The user's date of birth.
    :type birthdate: date
    :param additional_data: Additional data about the user.
    :type additional_data: str, optional
    """
    id: int
    id: int
    name: str
    surname: Optional[str]
    email: EmailStr
    phone: str
    birthdate: date
    additional_data: Optional[str]

    class Config:
        from_attributes = True


class UserUpdate(UserModel):
    """
    Represents a model for updating user data.
    """
    ...


class UserNameQuery(BaseModel):
    """
    Represents a model for querying users by username.

    :param user_name: The username to query.
    :type user_name: str
    """
    user_name: str


class AccountModel(BaseModel):
    """
    Represents a model for account data.

    :param login: The account's login username.
    :type login: str
    :param email: The account's email address.
    :type email: str
    :param password: The account's password.
    :type password: str
    """
    login: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=6, max_length=15)


class AccountDb(BaseModel):
    """
    Represents a model for account database data.

    :param id: The account's ID.
    :type id: int
    :param login: The account's login username.
    :type login: str
    :param email: The account's email address.
    :type email: str
    :param avatar: The URL of the account's avatar image.
    :type avatar: str
    """
    id: int
    login: str
    email: str
    avatar: str

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    """
    Represents a model for account response data.

    :param login: The account information.
    :type login: AccountDb
    :param detail: Additional detail message (default: "Account successfully created").
    :type detail: str
    """
    login: AccountDb
    detail: str = "Account successfully created"


class TokenModel(BaseModel):
    """
    Represents a model for token data.

    :param access_token: The access token.
    :type access_token: str
    :param refresh_token: The refresh token.
    :type refresh_token: str
    :param token_type: The type of token (default: "bearer").
    :type token_type: str
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Represents a model for requesting an email.

    :param email: The email address to request.
    :type email: EmailStr
    """
    email: EmailStr
