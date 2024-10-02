from uuid import UUID

from pydantic import BaseModel


class FriendRequestSent(BaseModel):
    """User отправил запрос на дружбу"""

    sender: UUID
    recipient: UUID
    msg: str = "The friendship request has been sent. After confirmation, you will become friends!"
