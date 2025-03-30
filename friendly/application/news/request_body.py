from uuid import UUID

from application.news.schemas import NewsBodyInfo
from pydantic import Field, conlist


class CreateNews(NewsBodyInfo):
    attachments: conlist(UUID, min_length=0, max_length=5) = Field(
        description="A list with the ID's of attachments, stored on the server.",
        examples=[["9ece8668-8ff0-4c70-ba90-482b0d134dd2", "00753fdd-cccb-40b7-8786-bac2c5ed287a"]],
        default=[],
    )
