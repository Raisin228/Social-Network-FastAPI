from datetime import datetime
from enum import StrEnum

from application.core.model_types import id_pk, userId_fk
from database import Base
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class NotificationStatus(StrEnum):
    UNREAD = "UNREAD"
    READ = "READ"


class FirebaseDeviceToken(Base):
    __tablename__ = "firebaseDeviceToken"

    id: Mapped[id_pk]
    holder_id: Mapped[userId_fk]
    device_token: Mapped[str] = mapped_column(String(256), nullable=False)


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[id_pk]
    sender: Mapped[userId_fk]
    recipient: Mapped[userId_fk]
    title: Mapped[str] = Column(String(128), nullable=True)
    text: Mapped[str] = Column(String(500), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = Column(String(6), server_default=NotificationStatus.UNREAD)
