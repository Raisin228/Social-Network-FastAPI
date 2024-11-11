from datetime import datetime
from enum import StrEnum

from application.core.model_types import id_pk, userId_fk
from database import Base
from sqlalchemy import CheckConstraint, Column, String, text
from sqlalchemy.orm import Mapped, mapped_column


class NotificationStatus(StrEnum):
    UNREAD = "UNREAD"
    READ = "READ"


class FirebaseDeviceToken(Base):
    """Токены устройств, подключенных к FCM"""

    __tablename__ = "firebaseDeviceToken"

    id: Mapped[id_pk]
    holder_id: Mapped[userId_fk]
    device_token: Mapped[str] = mapped_column(String(256), nullable=False)

    __table_args__ = (CheckConstraint("char_length(device_token) >= 140", name="min_device_token_len_140"),)


class Notification(Base):
    """Уведомления, отправленные пользователям"""

    __tablename__ = "notification"

    id: Mapped[id_pk]
    sender: Mapped[userId_fk]
    recipient: Mapped[userId_fk]
    title: Mapped[str] = Column(String(128), nullable=False)
    message: Mapped[str] = Column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    status: Mapped[str] = Column(String(6), server_default=NotificationStatus.UNREAD)

    __table_args__ = (
        CheckConstraint(
            "created_at >= DATE '1900-01-01' AND created_at <= CURRENT_TIMESTAMP", name="check_created_at_1900"
        ),
    )
