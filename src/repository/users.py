import datetime
from sqlalchemy import extract, or_, and_
from sqlalchemy.orm import Session
from src.database.models import User, Account
from src.schemas import UserModel, UserUpdate


async def get_users(skip: int, limit: int, account: Account, db: Session):
    """
    Returns a list of users from the database.
    
    :param skip: Skip the first n users in the database
    :type skip: int
    :param limit: Limit the number of users returned
    :type limit: int
    :param account: User account
    :type account: Account
    :param db: DB session
    :type db: Session
    :return: A list of user objects
    :rtype: list[User]
    """
    return db.query(User).filter(User.account_id == account.id).offset(skip).limit(limit).all()


async def get_user(user_id: int, account: Account, db: Session):
    """
    Returns a user object from the database.
    
    :param user_id: int: User ID
    :type user_id: int
    :param account: User account
    :type account: Account
    :param db: DB session
    :type db: Session
    :return: A user object
    :rtype: User
    """
    return db.query(User).filter(and_(User.id == user_id, User.account_id == account.id)).first()


async def find_user(user_name: str, user_surname: str, user_email: str, account: Account, db: Session):
    """
    Finds a user by their first name, last name, and email address for the specified account
    
    :param user_name: Filter the query by user name
    :type user_name: str
    :param user_surname: sFilter the users by surname
    :type user_surname: str
    :param user_email: Filter the query by email
    :type user_email: str
    :param account: User account
    :type account: Account
    :param db: DB session
    :type db: Session
    :return: The first user found in the database with the given parameters
    :rtype: User
    """
    query = db.query(User)

    if user_name is not None:
        query = query.filter(and_(User.name == user_name, User.account_id == account.id))
    if user_surname is not None:
        query = query.filter(and_(User.surname == user_surname, User.account_id == account.id))
    if user_email is not None:
        query = query.filter(and_(User.email == user_email, User.account_id == account.id))

    return query.first()


async def upcoming_birthdays(db: Session, account: Account, days: int = 7):
    """
    Returns a list of users whose birthdays are within the next 7 days
    
    :param db: DB session
    :type db: Session
    :param account: User account
    :type account: Account
    :param days: Determine how many days in the future to look for upcoming birthdays
    :type days: int
    :return: A list of users
    :rtype: list[User]
    """
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
    """
    Creates a new user for current Account
    
    :param body: Get the data from the request body
    :type body: UserModel
    :param current_user: Get the current user that is logged in
    :type current_user: Account
    :param db: DB session
    :type db: Session
    :return: New user
    :rtype: User
    """
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
    """
    Removes a user from the database.
    
    :param user_id: Identify the user to be removed
    :type user_id: int
    :param account: User account
    :type account: Account
    :param db: DB session
    :type db: Session
    :return: Removed user object or None (if user not exist)
    :rtype: User or None
    """
    user = db.query(User).filter(and_(User.id == user_id, User.account_id == account.id)).first()
    if user:
        db.delete(user)
        db.commit()
    return user


async def update_user(user_id: int, body: UserUpdate, account: Account, db: Session):
    """
    Updates a user in the database.
    
    :param user_id: Identify the user to be updated
    :type user_id: int
    :param body: Updated user's data
    :type body: UserUpdate
    :param account: User account
    :type account: Account
    :param db: DB session
    :type db: Session
    :return: Updated user object or None (if user not exist)
    :rtype: User or None
    """
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
