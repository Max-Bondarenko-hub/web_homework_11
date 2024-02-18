from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import UserModel, UserResponse, UserUpdate
from src.repository import users as users_repo


router = APIRouter(prefix="/users")


@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = await users_repo.get_users(skip, limit, db)
    return users


@router.get("/{user_id:int}", response_model=UserResponse)
async def read_users(user_id: int, db: Session = Depends(get_db)):
    user = await users_repo.get_user(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/find", response_model=UserResponse)
async def find_user(
    user_name: str = Query(title="User Name", default=None),
    user_surname: str = Query(title="User Surname", default=None),
    user_email: str = Query(title="User Email", default=None),
    db: Session = Depends(get_db)
):
    user = await users_repo.find_user(user_name, user_surname, user_email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(body: UserUpdate, user_id: int, db: Session = Depends(get_db)):
    user = await users_repo.update_user(user_id, body, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(body: UserModel, db: Session = Depends(get_db)):
    return await users_repo.create_user(body, db)


@router.get("/upcoming-birthdays", response_model=List[UserResponse])
async def upcoming_birthdays_list(db: Session = Depends(get_db)):
    users = await users_repo.upcoming_birthdays(db)
    return users


@router.delete("/{user_id}", response_model=UserResponse)
async def remove_user(user_id: int, db: Session = Depends(get_db)):
    user = await users_repo.remove_user(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
