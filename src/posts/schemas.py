from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class DoPost(BaseModel):
    topic: str = None
    main_text: str
    image_url: HttpUrl
    created_at: datetime = Field(default=datetime.utcnow)
