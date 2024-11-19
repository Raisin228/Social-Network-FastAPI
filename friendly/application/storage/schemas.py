from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class FileSavedOnCloud(BaseModel):
    msg: Literal["The file was saved successfully"] = "The file was saved successfully"
    link_to_file: HttpUrl = Field(
        description="Link to access the file", examples=["https://storage.yandexcloud.net/friendly-files-storage/..."]
    )


class FileRemoved(BaseModel):
    msg: Literal["The file was successfully deleted. All links referring to it are now broken"] = (
        "The file was successfully " "deleted. All links " "referring to it are now " "broken"
    )
    file_id: UUID = Field(description="Id of the file in the database.")
    name: str = Field(description="Alias file on the server.", min_length=6, max_length=32)
    created_at: datetime = Field(
        description="The timestamp when the object was created. Automatically set to the current UTC time."
    )
    size: float = Field(description="The file size in MB.", examples=[18.4])
    # продолжаем тут хотел сделать огранич
