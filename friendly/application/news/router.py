from datetime import datetime, timezone
from typing import List
from uuid import UUID

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from application.news.dao import NewsDao, NewsFilesDao
from application.news.request_body import CreateNews
from application.news.schemas import FullNewsInfo, NewsRemoved
from database import Transaction
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/news", tags=["News"])


@router.post(
    "/produce_content",
    summary="Create a new post on my wall",
    responses=UNAUTHORIZED | BAD_REQUEST | FORBIDDEN,
    response_model=FullNewsInfo,
)
async def create_news(news_info: CreateNews, user: User = Depends(get_current_user_access_token)):
    """Создание поста на странице от личной учётной записи"""

    data = dict(news_info)
    data["user_id"] = user.id
    pinning_data = data.pop("attachments")

    async with Transaction() as session:
        news = await NewsDao.add(session, data)
        news_body = news.to_dict()
        is_attached = await __link_post_with_files(pinning_data, news.id, session)

        if not is_attached:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="It's possible that incorrect file ID's were specified or "
                "files no longer exist.",
            )
        await session.refresh(news)
        files = list(
            map(
                lambda m: {"file_id": m.id, "link_to_file": m.s3_path, "filename": m.name},
                news.attachments,
            )
        )

    return FullNewsInfo(
        **{
            "news_id": news_body["id"],
            "topic": news_body["topic"],
            "main_text": news_body["main_text"],
            "owner_id": news_body["user_id"],
            "created_at": news_body["created_at"],
            "updated_at": news_body["updated_at"],
            "attachments": files,
        }
    )


@router.delete(
    "/erase_post/{post_id}",
    responses=NOT_FOUND | FORBIDDEN | UNAUTHORIZED,
    response_model=NewsRemoved,
)
async def destroy_news(post_id: UUID, user: User = Depends(get_current_user_access_token)):
    """Удалить пост, созданный пользователем"""

    async with Transaction() as session:
        post = await NewsDao.find_by_filter(session, {"id": post_id})

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No records could be found for the specified ID. There is probably a typo "
                "in the post_id.",
            )

    post_owner_id = post.get("user_id")
    if post_owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are trying to delete a news item created by another user. "
            "The operation is impossible. You must be the creator of the post.",
        )

    async with Transaction() as session:
        deleted_post = (await NewsDao.delete_by_filter(session, {"id": post_id}))[0]

    return NewsRemoved(
        **{
            "news_id": post_id,
            "topic": deleted_post.get("topic"),
            "main_text": deleted_post.get("main_text"),
            "deleted_at": datetime.now(timezone.utc),
        }
    )


# делаем получение новостей


# todo возможно следует вынести в utils
# todo можно сделать удаление записи о файле из таблицы file если файл удалили с облака
async def __link_post_with_files(
    link_ids: List[UUID], news_identity: UUID, session: AsyncSession
) -> bool:
    """Связываем вложения с постами"""
    data_for_saving = []
    for link_id in link_ids:
        data_for_saving.append({"news_id": news_identity, "file_id": link_id})
    try:
        await NewsFilesDao.add(session, data_for_saving)
    except IntegrityError:
        return False
    return True
