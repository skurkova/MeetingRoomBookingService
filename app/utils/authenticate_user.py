from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.get_user import get_user
from app.utils.security_password import verify_password


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """Аутентификация пользователя"""

    user = await get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
