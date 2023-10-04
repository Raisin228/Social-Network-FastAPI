from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.models import User
from database import get_async_session
from posts.models import news
from posts.schemas import DoPost

current_user = fastapi_users.current_user()
news_router = APIRouter(
    prefix='/news_tape',
    tags=['News']
)


@news_router.post('/feed')
async def add_news(data: DoPost, user: User = Depends(current_user),
                   session: AsyncSession = Depends(get_async_session)):
    """Добавить новость"""

    dict_data = dict(data)
    # добавляем id пользователя и приводим данные к типам в бд
    dict_data['user_id'] = user.id
    dict_data['image_url'] = str(dict_data['image_url'])
    stmt = insert(news).values(**dict_data)
    await session.execute(stmt)
    await session.commit()
    return {'status': 200, 'msg': data}


