import datetime
from sqlalchemy import extract, or_, and_
from sqlalchemy.orm import Session
from src.database.models import User, Account
from src.schemas import UserModel, UserUpdate


async def get_users(skip: int, limit: int, account: Account, db: Session):
    return db.query(User).filter(User.account_id == account.id).offset(skip).limit(limit).all()


async def get_user(user_id: int, account: Account, db: Session):
    return db.query(User).filter(and_(User.id == user_id, User.account_id == account.id)).first()


async def find_user(user_name: str, user_surname: str, user_email: str, account: Account, db: Session):
    query = db.query(User)

    if user_name is not None:
        query = query.filter(and_(User.name == user_name, User.account_id == account.id))
    if user_surname is not None:
        query = query.filter(and_(User.surname == user_surname, User.account_id == account.id))
    if user_email is not None:
        query = query.filter(and_(User.email == user_email, User.account_id == account.id))

    return query.first()


async def upcoming_birthdays(db: Session, account: Account, days: int = 7):
    current_date = datetime.date.today()
    end_date = current_date + datetime.timedelta(days=days)

    condition = or_(
        and_(
            extract("month", User.birthdate) == current_date.month, extract("day", User.birthdate) >= current_date.day
        ),
        and_(extract("month", User.birthdate) == end_date.month, extract("day", User.birthdate) <= end_date.day),
    )

    return db.query(User).filter(and_(condition, User.account_id == account.id)).all()


async def create_user(body: UserModel, current_user: Account, db: Session):
    user = User(
        name=body.name,
        surname=body.surname,
        email=body.email,
        phone=body.phone,
        birthdate=body.birthdate,
        additional_data=body.additional_data,
        account_id=current_user.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def remove_user(user_id: int, account: Account, db: Session):
    user = db.query(User).filter(and_(User.id == user_id, User.account_id == account.id)).first()
    if user:
        db.delete(user)
        db.commit()
    return user


async def update_user(user_id: int, body: UserUpdate, account: Account, db: Session):
    user = db.query(User).filter(and_(User.id == user_id, User.account_id == account.id)).first()
    if user:
        user.name = body.name
        user.surname = body.surname
        user.email = body.email
        user.phone = body.phone
        user.birthdate = body.birthdate
        user.additional_data = body.additional_data
        db.commit()
    return user
