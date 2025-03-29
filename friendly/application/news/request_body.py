from uuid import UUID

from pydantic import BaseModel, Field, conlist


class CreateNews(BaseModel):
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
    attachments: conlist(UUID, min_length=0, max_length=5) = Field(
        description="A list with the ID's of attachments, stored on the server.",
        examples=[["9ece8668-8ff0-4c70-ba90-482b0d134dd2", "00753fdd-cccb-40b7-8786-bac2c5ed287a"]],
        default=[],
    )
