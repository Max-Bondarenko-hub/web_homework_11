import cloudinary
import cloudinary.uploader

from fastapi import UploadFile, File, APIRouter, Depends

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.conf.config import settings
from src.repository import accounts
from src.schemas import AccountDb
from src.services.auth import auth_service
from src.database.models import Account


router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/my_profile", response_model=AccountDb)
async def read_users_me(current_user: Account = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=AccountDb)
async def update_avatar_user(file: UploadFile = File(), current_user: Account = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'Profile/{current_user.login}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'Profile/{current_user.login}').build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await accounts.update_avatar(current_user.email, src_url, db)
    return user