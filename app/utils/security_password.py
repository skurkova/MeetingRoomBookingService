from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_the_password(password: str) -> str:
    """Хешируем пароль"""

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяем пароль"""

    return pwd_context.verify(password, hashed_password)
