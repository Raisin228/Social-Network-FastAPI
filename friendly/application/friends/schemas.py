from uuid import UUID

from application.profile.request_body import MinUserInformation
from pydantic import BaseModel, Field


class FriendRequestSent(BaseModel):
    """User отправил запрос на дружбу (ответ от сервера)"""

    sender: UUID = Field(description="The ID of the user who made the request")
    recipient: UUID = Field(description="Who was the friend request sent to")
    msg: str = "The friendship request has been sent. After confirmation, you will become friends!"


class UserWithFriendStatus(MinUserInformation):
    """Пользователь с мин.информацией и статусом дружбы"""

    status: str = Field(
        examples=["NOT_APPROVE"],
        description="Current status of the appeal",
        max_length=11,
        min_length=6,
    )


class IncomeRequests(UserWithFriendStatus):
    """Входящий запрос на дружбу (который получил я)"""

    sender_id: UUID = Field(description="The ID of the user who made the request")


class Friend(UserWithFriendStatus):
    """Пользователь, являющийся другом"""

    friend_id: UUID = Field(description="Your friend's ID")


class ApplyFriend(BaseModel):
    """Принял запрос на дружбу"""

    friend_id: UUID = Field(description="Now you are friends with this user")
    msg: str = "You become friends!"


class DeleteFriendship(BaseModel):
    """Пользователь больше не является нашим другом"""

    former_friend_id: UUID = Field(description="ID of a former friend")
    msg: str = "The user has been removed from the friends list"


class UserBlockUnblock(BaseModel):
    """Пользователь заблокирован | разблокирован"""

    msg: str
    block_user_id: UUID
