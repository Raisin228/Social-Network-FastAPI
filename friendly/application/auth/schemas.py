from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str | None
    last_name: str | None
    login: str
