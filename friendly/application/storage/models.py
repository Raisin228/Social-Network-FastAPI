from datetime import datetime

from application.core.model_types import id_pk, userId_fk
from database import Base
from sqlalchemy import UUID, CheckConstraint, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column


class FileType(Base):
    __tablename__ = "fileType"
    id: Mapped[id_pk]
    obj_type: Mapped[str] = MappedColumn(String(20), nullable=False)
    __table_args__ = (CheckConstraint("char_length(obj_type) >= 3", name="min_obj_type_len_3"),)


class File(Base):
    __tablename__ = "file"
    id: Mapped[id_pk]
    owner_id: Mapped[userId_fk]
    name: Mapped[str] = MappedColumn(String(32), nullable=False)
    s3_path: Mapped[str] = MappedColumn(String(2083), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    type_id: Mapped[UUID | None] = mapped_column(ForeignKey("fileType.id", ondelete="SET NULL"), nullable=True)
    size: Mapped[int] = MappedColumn(Integer, nullable=False)  # размер в байтах!

    __table_args__ = (CheckConstraint("char_length(name) >= 6", name="min_file_name_len_6"),)
