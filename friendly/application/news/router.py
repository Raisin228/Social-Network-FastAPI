from datetime import datetime, timezone
from uuid import UUID

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from application.news.constants import POST_NOT_FOUND
from application.news.dao import NewsDao, NewsFilesDao, UserNewsReactionDao
from application.news.models import ReactionType
from application.news.request_body import CreateNews
from application.news.schemas import (
    FullNewsInfo,
    NewsInfo,
    NewsRemoved,
    PostInformationWithAttachmentsReactions,
    ReactionsByPost,
)
from application.storage.schemas import MinFileInfo
from database import Transaction
from fastapi import APIRouter, Depends, HTTPException, status

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
        is_attached = await NewsFilesDao.link_post_with_files(pinning_data, news.id, session)

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


@router.post(
    "/add_reaction/{news_id}",
    responses=NOT_FOUND | FORBIDDEN | UNAUTHORIZED,
    response_model=ReactionsByPost,
)
async def leave_reaction_under_post(
    news_id: UUID, reaction_type: ReactionType, user: User = Depends(get_current_user_access_token)
):
    """Поставить реакцию под новостью, либо заменить существующую"""

    async with Transaction() as session:
        post = await NewsDao.find_by_filter(session, {"id": news_id})

        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=POST_NOT_FOUND)
        await UserNewsReactionDao.leave_reaction(session, user.id, news_id, reaction_type)

    all_reactions = await UserNewsReactionDao.list_reactions_under_post(session, user.id, news_id)
    return ReactionsByPost(news_id=news_id, total_reactions=all_reactions)


# TODO переделать
@router.get(
    "/feed/list", response_model=list[NewsInfo], responses=NOT_FOUND | FORBIDDEN | UNAUTHORIZED
)
async def get_news_id_list(
    usr_id: UUID | None = None, user: User = Depends(get_current_user_access_token)
):
    res = []
    search_filter = {"user_id": user.id if usr_id is None else usr_id}
    async with Transaction() as session:
        data = await NewsDao.find_by_filter(session, search_filter)

        if data is None:
            data = []
        elif isinstance(data, dict):
            data = [data]

        for rec in data:
            print(rec, type(rec), data)
            rec["news_id"] = rec.pop("id")
            rec["owner_id"] = rec.pop("user_id")

            res.append(NewsInfo.model_validate(rec))
    return res


# TODO: было решено вообще не делать пагинацию в данном методе (на стадии mvp) потому что нормальное
# внедрение пагинации через cursor потребует слишком большого времени (1) развалятся тесты и все
# существующие методы
# Делать временно пагинацию через limit offset нецелесообразно потому что впоследствии она будет
# удалена
# Пока данных мало просто делаем получение всех новостей по пользователю и получение всех реакций
# под каждым конкретным постом -> упаковываем в schema и отдаём в json
@router.get(
    "/feed/{news_id}",
    summary="Full information on a specific news item",
    responses=NOT_FOUND | FORBIDDEN | UNAUTHORIZED,
    response_model=PostInformationWithAttachmentsReactions,
)
# TODO метод и всё что с ним связано (схемы вызовы) дрянь -> делался на скорую руку ПЕРЕДЕЛАТЬ!!!
async def specific_news_information(
    news_id: UUID, user: User = Depends(get_current_user_access_token)
):
    async with Transaction() as session:
        post_body_info = await NewsDao.find_by_filter(session, {"id": news_id}, return_models=True)

        if post_body_info is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=POST_NOT_FOUND)

        reaction_under_post = await UserNewsReactionDao.list_reactions_under_post(
            session, user.id, news_id
        )

        files = list(
            map(
                lambda file_obj: MinFileInfo.model_validate(
                    {"file_id": file_obj.id, "link_to_file": file_obj.s3_path}
                ),
                post_body_info.attachments,
            )
        )

        body = NewsInfo(
            **{
                "news_id": post_body_info.id,
                "topic": post_body_info.topic,
                "main_text": post_body_info.main_text,
                "owner_id": post_body_info.user_id,
                "created_at": post_body_info.created_at,
                "updated_at": post_body_info.updated_at,
            }
        )

        res = PostInformationWithAttachmentsReactions.model_validate(
            {"post_body": body, "attachments": files, "reactions": reaction_under_post}
        )

    return res


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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=POST_NOT_FOUND)

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


# todo можно сделать удаление записи о файле из таблицы file если файл удалили с облака
# todo была какое то предупреждение о закрытии transaction
# todo думай над оптимизацией базы и запросов (как минимум очень много мест с запросами в цикле)
# todo нужен метод который позволит удалить реакцию


# todo testы для всех методов
