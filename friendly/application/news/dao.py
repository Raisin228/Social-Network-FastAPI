from typing import List
from uuid import UUID

from application.news.models import (
    News,
    NewsFiles,
    Reaction,
    ReactionType,
    UserNewsReaction,
)
from data_access_object.base import BaseDAO
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class NewsDao(BaseDAO):
    model = News


class NewsFilesDao(BaseDAO):
    model = NewsFiles

    @classmethod
    async def link_post_with_files(
        cls, link_ids: List[UUID], news_identity: UUID, session: AsyncSession
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


class ReactionDao(BaseDAO):
    model = Reaction


class UserNewsReactionDao(BaseDAO):
    model = UserNewsReaction

    @classmethod
    async def list_reactions_under_post(cls, session: AsyncSession, usr_id: UUID, news_id: UUID):
        """
        Получить список реакций под постом
        # todo капец какой не эффективный метод
        """
        result = []
        existing_reactions = await ReactionDao.find_by_filter(session, {})

        for reaction in existing_reactions:
            r_id, r_type = reaction.get("id"), reaction.get("type")
            is_reacted = False
            search_param = {"news_id": news_id, "reaction_type_id": r_id}
            data = await UserNewsReactionDao.find_by_filter(session, search_param)

            if data is None:
                continue

            if isinstance(data, dict):
                quantity = 1
            else:
                quantity = len(data)

            search_param["user_id"] = usr_id
            info = await UserNewsReactionDao.find_by_filter(session, search_param)
            if info is not None:
                is_reacted = True

            record = {
                "reaction_id": r_id,
                "type": r_type,
                "emoji": ReactionType(r_type).convert_letter_type_to_emoji(),
                "count": quantity,
                "reacted_by_user": is_reacted,
            }
            result.append(record)
        result.sort(key=lambda emoji: (emoji.get("count", 0), emoji.get("type", "")), reverse=True)
        return result

    @classmethod
    async def leave_reaction(
        cls, session: AsyncSession, usr_id: UUID, news_id: UUID, emotion: ReactionType
    ) -> UserNewsReaction:
        """
        Оставить реакцию под выбранным постом. Если реакции ещё не было -> добавляем,
        иначе удаляем старую и оставляем новую.
        """
        income_param = {"news_id": news_id, "user_id": usr_id}
        is_usr_leave_reaction = await UserNewsReactionDao.find_by_filter(session, income_param)

        if is_usr_leave_reaction is None:
            added_reaction = await cls.__add_reaction(session, emotion, income_param)
        else:
            await UserNewsReactionDao.delete_by_filter(session, income_param)
            added_reaction = await cls.__add_reaction(session, emotion, income_param)
        return added_reaction

    @classmethod
    async def __add_reaction(
        cls, session: AsyncSession, emotion_type: ReactionType, additional_params: dict
    ) -> UserNewsReaction:
        """
        Добавить новую реакцию. Для начала нужно получить ID реакции из БД а
        потом добавить как обычно
        """
        reaction_rec_from_db = await ReactionDao.find_by_filter(
            session, {"type": emotion_type.value}
        )
        prep_data_new_reaction = additional_params
        prep_data_new_reaction["reaction_type_id"] = reaction_rec_from_db.get("id")
        new_reaction = await UserNewsReactionDao.add(session, prep_data_new_reaction)
        return new_reaction
