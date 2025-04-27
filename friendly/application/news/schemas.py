from datetime import datetime
from typing import List, Literal
from uuid import UUID

from application.storage.schemas import MinFileInfo
from pydantic import BaseModel, Field


class NewsBodyInfo(BaseModel):
    """Тело новости"""

    topic: str = Field(
        min_length=6,
        max_length=50,
        examples=["My first normal job"],
        description="The headline of the news. Something memorable and challenging!",
    )
    main_text: str = Field(
        min_length=6,
        max_length=2200,
        examples=[
            "And finally... I got a position as an engineer. "
            "I'm eager to get rich immediately. "
            "This is my first day as the master of the universe."
        ],
        description="The main text part of the news.",
    )


class NewsInfo(NewsBodyInfo):
    """Все данные из тела поста"""

    news_id: UUID = Field(
        description="News unique identifier", examples=["e7e7dc03-25fb-49d4-bceb-9cf871031aea"]
    )
    owner_id: UUID = Field(
        description="News creator", examples=["e7e8dc13-25fb-49d4-bceb-9cf871031aea"]
    )
    created_at: datetime = Field(
        description="Date of the first publication of the news",
        examples=["2006-10-100T15:17:10.093545"],
    )
    updated_at: datetime | None = Field(
        description="Date of last news update", examples=["2025-03-30T15:17:10.093545"]
    )


class FullNewsInfo(NewsBodyInfo):
    """Исчерпывающая информация о содержании новости вместе со вложениями"""

    attachments: List[MinFileInfo]


class NewsRemoved(NewsBodyInfo):
    """Новость была успешно удалена"""

    msg: Literal["The news was successfully deleted"] = "The news was successfully deleted."
    news_id: UUID = Field(description="Id of the news in the database.")
    deleted_at: datetime = Field(
        description="Time to delete an entry.", examples=["2025-03-30T15:17:10.093545"]
    )


class SpecificReaction(BaseModel):
    """Data on one specific reaction"""

    reaction_id: UUID = Field(
        description="Unique reaction identifier", examples=["e7e8dc13-25fb-49d4-bceb-9cf871031aea"]
    )
    type: str = Field(
        min_length=3, max_length=20, description="Emoji type", examples=["LIKE", "FIRE"]
    )
    emoji: str = Field(description="Emojis to display on the UI", examples=["👍", "🔥"])
    count: int = Field(description="The number of users who left a reaction", examples=[29])
    reacted_by_user: bool = Field(
        description="Has this user left a reaction?", examples=[True, False]
    )


class ReactionsByPost(BaseModel):
    """All reaction added to the post"""

    news_id: UUID = Field(
        description="News unique identifier", examples=["e7e7dc03-25fb-49d4-bceb-9cf871031aea"]
    )
    total_reactions: List[SpecificReaction] = Field(
        description="All information about the reactions left"
    )


class PostInformationWithAttachmentsReactions(BaseModel):
    """Полная информация по посту + вложения и реакции"""

    post_body: NewsInfo
    attachments: List[MinFileInfo]
    reactions: List[SpecificReaction]
