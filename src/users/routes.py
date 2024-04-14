import pickle
import fastapi

import cloudinary
import cloudinary.uploader

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.auth.models import User
from src.auth.schemas import UserResponse
from src.auth.services import auth_service
from src.config import config

import src.users.crud as repository_users


router = fastapi.APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[fastapi.Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = fastapi.Depends(auth_service.get_current_user)):
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[fastapi.Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
    file: fastapi.UploadFile = fastapi.File(),
    user: User = fastapi.Depends(auth_service.get_current_user),
    db: AsyncSession = fastapi.Depends(get_db),
):
    public_id = f"HW13/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
