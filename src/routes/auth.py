from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.schemas import AccountModel, AccountResponse, TokenModel, RequestEmail
from src.repository import accounts
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=AccountResponse, status_code=status.HTTP_201_CREATED, 
            description='No more than 1 account per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))]
)
async def signup(body: AccountModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    :param body: Data of the new user account.
    :type body: AccountModel
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request: FastAPI request.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: Details of the created user account.
    :rtype: dict
    """
    exist_account = await accounts.get_user_by_email(body.email, db)
    if exist_account:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_account = await accounts.create_account(body, db)
    background_tasks.add_task(send_email, new_account.email, new_account.login, request.base_url)
    return {"login": new_account, "detail": "Account successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    User login.

    :param body: Login form data.
    :type body: OAuth2PasswordRequestForm
    :param db: Database session.
    :type db: Session
    :return: Access token and refresh token.
    :rtype: TokenModel
    """
    acc = await accounts.get_email_by_username(body.username, db)
    user = await accounts.get_user_by_email(acc.email, db)
    print(type(body.username))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email!")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await accounts.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refresh user access token.

    :param credentials: HTTP credentials.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Database session.
    :type db: Session
    :return: Access token and refresh token.
    :rtype: TokenModel
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await accounts.get_user_by_email(email, db)
    if user.refresh_token != token:
        await accounts.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await accounts.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm user email address.

    :param token: Token for email address confirmation.
    :type token: str
    :param db: Database session.
    :type db: Session
    :return: Confirmation message.
    :rtype: dict
    """
    email = await auth_service.get_email_from_token(token)
    print("email ", email)
    user = await accounts.get_user_by_email(email, db)
    if user is None:
        print("user error")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        print("conf error")
        return {"message": "Your email is already confirmed"}
    await accounts.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)
):
    """
    Send request for email address confirmation.

    :param body: Data of request for email address confirmation.
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request: FastAPI request.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: Message about request for email address confirmation.
    :rtype: dict
    """
    user = await accounts.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.login, request.base_url)
    return {"message": "Check your email for confirmation."}
