import uuid
from typing import List

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.responses import UNAUTHORIZED
from application.news.dao import NewsDao, NewsFilesDao
from application.news.request_body import CreateNews
from database import Transaction, get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/news", tags=["News"])


@router.post("/produce_content", summary="Create a new post on my wall", responses=UNAUTHORIZED)
async def create_news(
    news_info: CreateNews,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Создание поста на странице от личной учётной записи"""

    data = dict(news_info)
    data["user_id"] = user.id
    pinning_data = data.pop("attachments")

    async with Transaction() as session:
        result = await NewsDao.add(session, data)
        await __link_post_with_files(pinning_data, result.id, session)


async def __link_post_with_files(link_ids: List[uuid.UUID], news_identity: uuid.UUID, session: AsyncSession):
    """Связываем вложения с постами"""
    data_for_saving = []
    for link_id in link_ids:
        data_for_saving.append({"news_id": news_identity, "file_id": link_id})

    info = await NewsFilesDao.add(session, data_for_saving)
    print(info)
