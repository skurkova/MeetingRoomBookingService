from pydantic import BaseModel, EmailStr, ConfigDict


class UserResponse(BaseModel):
    """Схема для отображения информации о пользователе"""

    id: int
    username: str
    full_name: str
    email: EmailStr
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)
