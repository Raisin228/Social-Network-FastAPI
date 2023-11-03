from datetime import datetime

from pydantic import BaseModel, HttpUrl
from typing_extensions import Optional


class DoPost(BaseModel):
    """Схема для валидации входящих данных от пользователя для создания поста"""
    topic: Optional[str] = None
    main_text: str
    image_url: HttpUrl


class ResponsePostCreated(BaseModel):
    """Новость успешно создана"""
    topic: Optional[str] = None
    main_text: str
    image_url: HttpUrl
    created_at: datetime
    updated_at: Optional[datetime] = None
    quantity_like: int = 0


class ResponseGetNews(ResponsePostCreated):
    """Схема получения массива новостей/понравившихся постов"""
    id: int
    user_id: int


class ResponseLikePost(BaseModel):
    """Схема ответа на лайкнутую запись"""
    detail: str
