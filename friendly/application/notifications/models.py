import uuid

from database import Base
from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column


class FirebaseDeviceToken(Base):
    __tablename__ = "firebaseDeviceToken"

    id: Mapped[uuid.UUID] = MappedColumn(UUID(as_uuid=True), primary_key=True, insert_default=uuid.uuid4)
    holder_id: Mapped[uuid.UUID] = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    device_token: Mapped[str] = mapped_column(String(256), nullable=False)
