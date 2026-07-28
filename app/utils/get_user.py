from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user(db: AsyncSession, username: str) -> User | None:
    """Получить пользователя в БД по username"""

    user = await db.execute(select(User).where(User.username == username))
    return user.scalar_one_or_none()
