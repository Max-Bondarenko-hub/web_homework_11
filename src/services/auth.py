from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import accounts
from src.conf.config import settings


class Auth:
    """
    Provides authentication and token management functionality.

    Attributes:
        pwd_context (CryptContext): Password hashing context.
        SECRET_KEY (str): Secret key for token encoding and decoding.
        ALGORITHM (str): Algorithm used for token encoding and decoding.
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer scheme.

    Methods:
        verify_password: Verify a plain password against a hashed password.
        get_password_hash: Generate a hashed password from a plain password.
        create_access_token: Create an access token with the given data and expiration delta.
        create_refresh_token: Create a refresh token with the given data and expiration delta.
        decode_refresh_token: Decode a refresh token to retrieve the email.
        get_current_user: Retrieve the current user from the access token.
        create_email_token: Create an email verification token with the given data.
        get_email_from_token: Retrieve the email from an email verification token.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        :param plain_password: Plain text password.
        :type plain_password: str
        :param hashed_password: Hashed password.
        :type hashed_password: str
        :return: True if the plain password matches the hashed password, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a hashed password from a plain password.

        :param password: Plain text password.
        :type password: str
        :return: Hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create an access token with the given data and expiration delta.

        :param data: Data to be encoded into the token.
        :type data: dict
        :param expires_delta: Expiration time delta in seconds.
        :type expires_delta: Optional[float]
        :return: Encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a refresh token with the given data and expiration delta.

        :param data: Data to be encoded into the token.
        :type data: dict
        :param expires_delta: Expiration time delta in seconds.
        :type expires_delta: Optional[float]
        :return: Encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode a refresh token to retrieve the email.

        :param refresh_token: Refresh token to decode.
        :type refresh_token: str
        :return: Decoded email.
        :rtype: str
        :raises HTTPException: If the token validation fails.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "refresh_token" and "sub" in payload:
                email = payload["sub"]
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Retrieve the current user from the access token.

        :param token: Access token.
        :type token: str
        :param db: Database session.
        :type db: Session
        :return: Current authenticated user.
        :rtype: Account
        :raises HTTPException: If the token validation fails or the user does not exist.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await accounts.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    

    def create_email_token(self, data: dict):
        """
        Retrieve the current user from the access token.

        :param token: Access token.
        :type token: str
        :param db: Database session.
        :type db: Session
        :return: Current authenticated user.
        :rtype: Account
        :raises HTTPException: If the token validation fails or the user does not exist.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    

    async def get_email_from_token(self, token: str):
        """
        Retrieve the email from an email verification token.

        :param token: Email verification token.
        :type token: str
        :return: Email extracted from the token.
        :rtype: str
        :raises HTTPException: If the token validation fails.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
