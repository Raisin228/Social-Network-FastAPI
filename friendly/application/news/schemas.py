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


class FullNewsInfo(NewsBodyInfo):
    """Исчерпывающая информация о содержании новости вместе со вложениями"""

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
    attachments: List[MinFileInfo]


class NewsRemoved(NewsBodyInfo):
    """Новость была успешно удалена"""

    msg: Literal["The news was successfully deleted"] = "The news was successfully deleted."
    news_id: UUID = Field(description="Id of the news in the database.")
    deleted_at: datetime = Field(
        description="Time to delete an entry.", examples=["2025-03-30T15:17:10.093545"]
    )
