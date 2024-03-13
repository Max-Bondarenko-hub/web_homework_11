from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import Account
from src.schemas import AccountModel


async def get_user_by_email(email: str, db: Session):
    """
    Get user name by email

    :param email: user email
    :type email: str
    :param db: DB session
    :type db: Session
    :return: User name
    :rtype: Account
    """
    result = db.query(Account).filter(Account.email == email).first()
    return result


async def get_email_by_username(username: str, db: Session):
    """
    Get user email by name

    :param username: User name
    :type username: str
    :param db: Session
    :type db: Session
    :return: User email
    :rtype: Account
    """
    result = db.query(Account).filter(Account.login == username).first()
    return result


async def create_account(body: AccountModel, db: Session):
    """
    Creates new account

    :param body: Scheme of account model
    :type body: AccountModel
    :param db: Session
    :type db: Session
    :return: New account
    :rtype: Account
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_account = Account(**body.dict(), avatar=avatar)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


async def update_token(login: Account, token: str | None, db: Session):
    """
    Update token for account

    :param login: Account
    :type login: Account
    :param token: new token or None
    :type token: str or None
    :param db: Session
    :type db: Session
    """
    login.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Sets the confirmed field of a user to True
    
    :param email: The email of the user
    :type email: str
    :param db: Pass the database session to the function
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session):
    """
    Updates the avatar of a user
    
    :param email: Find the user in the database
    :type email: str
    :param url: New avatar URL
    :type url: str
    :param db: Pass the database session to the function
    :type db: Session
    :return: The user object
    :rtype: Account
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
