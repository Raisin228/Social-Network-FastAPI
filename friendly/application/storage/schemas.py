from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class FileSavedOnCloud(BaseModel):
    msg: Literal["The file was saved successfully"] = "The file was saved successfully"
    link_to_file: HttpUrl = Field(
        description="Link to access the file", examples=["https://storage.yandexcloud.net/friendly-files-storage/..."]
    )
