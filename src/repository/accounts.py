from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import Account
from src.schemas import AccountModel


async def get_user_by_email(email: str, db: Session):
    result = db.query(Account).filter(Account.email == email).first()
    return result


async def get_email_by_username(username: str, db: Session):
    result = db.query(Account).filter(Account.login == username).first()
    return result


async def create_account(body: AccountModel, db: Session):
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
    login.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
