from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.logging import get_logger
from app.utils.get_user import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = get_logger(__name__)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """Получить текущего пользователя"""

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            await logger.info("Username is missing from the token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username is missing from the token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError:
        await logger.info("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        await logger.info("Invalid JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user(db=db, username=username)
    if user is None:
        await logger.info("User not found in database", username=username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is missing from the database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
