from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.crud import get_user_by_email


async def update_avatar_url(email: str, url: str | None, db: AsyncSession):
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
