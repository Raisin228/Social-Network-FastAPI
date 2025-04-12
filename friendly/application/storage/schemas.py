from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from config import settings
from pydantic import BaseModel, Field, HttpUrl, field_validator


class MinFileInfo(BaseModel):
    """Минимально допустимая информация о файле"""

    file_id: UUID = Field(description="Id of the file in the database.")
    link_to_file: HttpUrl = Field(
        description="Link to access the file",
        examples=["https://storage.yandexcloud.net/friendly-files-storage/..."],
    )


class FileSavedOnCloud(MinFileInfo):
    msg: Literal["The file was saved successfully"] = "The file was saved successfully"


class FileRemoved(BaseModel):
    msg: Literal["The file was successfully deleted. All links referring to it are now broken"] = (
        "The file was successfully " "deleted. All links " "referring to it are now " "broken"
    )
    file_id: UUID = Field(description="Id of the file in the database.")
    name: str = Field(description="Alias file on the server.", min_length=6, max_length=32)
    created_at: datetime = Field(
        description="The timestamp when the object was created. "
        "Automatically set to the current UTC time.",
        ge=datetime(1900, 1, 1, 0, 0, 0),
    )
    size: float = Field(
        description="The file size in MB.",
        examples=[18.4],
        ge=0,
        le=settings.FILE_MAX_SIZE_BYTE // 1024**2,
    )

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value):
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        if value > current_time:
            raise ValueError(f"'created_at' must be lower then now moment -> {current_time}")
        return value
