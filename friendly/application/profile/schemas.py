from typing import Literal

from application.auth.schemas import GetUser
from pydantic import BaseModel, ConfigDict, Field


class AccountDeleted(BaseModel):
    """Ответ сервера после удаления аккаунта"""

    msg: Literal["Account successfully deleted"] = Field(default="Account successfully deleted")
    deleted_account_info: GetUser

    model_config = ConfigDict(from_attributes=True, extra="forbid")
