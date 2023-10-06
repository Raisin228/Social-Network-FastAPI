from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import List, Union

from auth.base_config import fastapi_users
from auth.models import user
from bad_responses import Error400
from database import get_async_session
from posts.models import news, liked_posts
from posts.schemas import DoPost, ResponseGetNews, ResponsePostCreated, ResponseLikePost

# создаём новый роутер
current_user = fastapi_users.current_user()
news_router = APIRouter(
    prefix='/news_tape',
    tags=['News']
)


@news_router.get('/feed', response_model=List[ResponseGetNews],
                 responses={401: {'model': Error400, 'description': 'Unauthorized'}})
async def get_news(person: user = Depends(current_user),
                   session: AsyncSession = Depends(get_async_session)) -> list[dict]:
    """Получить ленту новостей"""
    query = select(news).order_by(desc(news.c.created_at))
    data = await session.execute(query)
    names_columns = list(data.keys())
    # приводим данные ответа в формат описаный в ResponseGetNews
    result = [dict(zip(names_columns, row)) for row in data]
    return result


@news_router.post('/feed', response_model=ResponsePostCreated,
                  responses={401: {'model': Error400, 'description': 'Unauthorized'}})
async def add_news(data: DoPost, person: user = Depends(current_user),
                   session: AsyncSession = Depends(get_async_session)) -> dict:
    """Добавить новость"""

    dict_data = dict(data)
    # добавляем id пользователя и приводим данные к типам в бд + генерируем время создания поста
    dict_data['user_id'] = person.id
    dict_data['image_url'] = str(dict_data.get('image_url'))
    dict_data['created_at'] = datetime.utcnow()
    # вставка и выполнение запроса
    stmt = insert(news).values(**dict_data)
    await session.execute(stmt)
    await session.commit()
    result = dict(data)
    result['created_at'] = dict_data['created_at']
    return result


@news_router.put('/like/{news_id}', response_model=ResponseLikePost,
                 responses={400: {"model": Error400, "description": "Item not found"},
                            401: {'model': Error400, 'description': 'Unauthorized'}})
async def like_chosen_post(news_id: int, person: user = Depends(current_user),
                           session: AsyncSession = Depends(get_async_session)) -> dict:
    """Эндпоинт для лайка записи"""
    # запрос на извлечение данных из таблицы liked_posts
    query = select(liked_posts).where(
        (liked_posts.c.user_id == person.id) & (liked_posts.c.post_id == news_id)
    )
    data = await session.execute(query)
    comp = data.fetchall()
    # если эта запись уже была лайкнута этим пользователем тогда like - 1
    if comp:
        stmt = update(news).where(news.c.id == news_id).values(quantity_like=news.c.quantity_like - 1)
        stmt2 = delete(liked_posts).where(
            (liked_posts.c.user_id == person.id) & (liked_posts.c.post_id == news_id)
        )
    # если не была тогда лайкаем пост
    else:
        # делаем запрос на проверку того что пост с таким id существует
        does_postid_exist = select(news).where(news.c.id == news_id)
        info_about_postid = await session.execute(does_postid_exist)
        if info_about_postid.fetchone():
            stmt = update(news).where(news.c.id == news_id).values(quantity_like=news.c.quantity_like + 1)
            stmt2 = insert(liked_posts).values(user_id=person.id, post_id=news_id)
        else:
            raise HTTPException(status_code=400, detail="Item not found")
    await session.execute(stmt)
    await session.execute(stmt2)
    await session.commit()
    return {'detail': 'OK'}


@news_router.get('/liked_posts', response_model=Union[List[ResponseGetNews], ResponseLikePost],
                 responses={401: {'model': Error400, 'description': 'Unauthorized'}})
async def get_liked_posts(person: user = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)) -> dict | list[dict]:
    """Список понравившихся постов"""
    # делаем запрос на получение id понравившихся постов
    query = select(liked_posts).where(liked_posts.c.user_id == person.id)
    data = await session.execute(query)
    # собираем список с id понравившихся постов
    id_liked_posts = [t[2] for t in data.fetchall()]

    # делаем запрос на получение постов с такими id если id_liked_posts ~ True
    if id_liked_posts:
        query2 = select(news).where(news.c.id.in_(id_liked_posts))
        ans = await session.execute(query2)
        names_columns = list(ans.keys())
        result = [dict(zip(names_columns, row)) for row in ans.fetchall()]
    # если id_liked_posts ~ False
    else:
        result = {'detail': 'No liked posts'}
    return result
