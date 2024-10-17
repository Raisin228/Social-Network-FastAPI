from datetime import datetime
from typing import Literal
from uuid import UUID

from application.notifications.models import NotificationStatus
from application.notifications.request_body import DeviceTokenFCM
from firebase.notification import NotificationEvent
from pydantic import BaseModel, Field


class FCMTokenSavedSuccess(DeviceTokenFCM):
    """Токен устройства успешно добавлен в бд"""

    msg: str = "This device is saved. Notifications will also be sent to him now."


class Notification(BaseModel):
    title: NotificationEvent = Field(description="Notification header")
    message: str = Field(
        description="Description of the notification",
        examples=["Пользователь [bog_at_04] хочет добавить вас в друзья."],
    )
    created_at: datetime = Field(description="Date the notification was created")
    status: NotificationStatus = Field(description="Current notification status")
    sender: UUID = Field(description="ID sender of the notification")
    id: UUID = Field(description="ID of the notification in the database")


class QuantityRemovedNotify(BaseModel):
    """Удалить все уведомления"""

    msg: Literal["Successful delete"] = Field(default="Successful delete")
    notify_removed: int = Field(1, description="Number of deleted notifications")
