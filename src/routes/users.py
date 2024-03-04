from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, UserUpdate
from src.repository import users as users_repo
from src.database.models import User, Account
from src.services.auth import auth_service


router = APIRouter(prefix="/users")


@router.get("/", response_model=List[UserResponse], 
            description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=5, seconds=60))]
            )
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Account = Depends(auth_service.get_current_user),
):
    users = await users_repo.get_users(skip, limit, current_user, db)
    return users


@router.get("/{user_id:int}", response_model=UserResponse)
async def read_users(
    user_id: int,
    db: Session = Depends(get_db), 
    current_user: Account = Depends(auth_service.get_current_user)
):
    user = await users_repo.get_user(user_id, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/find", response_model=UserResponse)
async def find_user(
    user_name: str = Query(title="User Name", default=None),
    user_surname: str = Query(title="User Surname", default=None),
    user_email: str = Query(title="User Email", default=None),
    db: Session = Depends(get_db),
    current_user: Account = Depends(auth_service.get_current_user)
):
    user = await users_repo.find_user(user_name, user_surname, user_email, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    body: UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(auth_service.get_current_user),
):
    user = await users_repo.update_user(user_id, body, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserModel, db: Session = Depends(get_db), current_user: Account = Depends(auth_service.get_current_user)
):
    return await users_repo.create_user(body, current_user, db)


@router.get("/upcoming-birthdays", response_model=List[UserResponse])
async def upcoming_birthdays_list(db: Session = Depends(get_db), current_user: Account = Depends(auth_service.get_current_user)):
    users = await users_repo.upcoming_birthdays(db, current_user)
    return users


@router.delete("/{user_id}", response_model=UserResponse)
async def remove_user(
    user_id: int, db: Session = Depends(get_db), current_user: Account = Depends(auth_service.get_current_user)
):
    user = await users_repo.remove_user(user_id, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
