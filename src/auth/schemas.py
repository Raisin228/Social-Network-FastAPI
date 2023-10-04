from fastapi_users import schemas
from typing_extensions import Optional


class UserRead(schemas.BaseUser[int]):
    """Данные отправляемые при чтении пользователя"""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    """Схема для отправки данных после создания акк. в системе"""
    username: str
    email: str
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
