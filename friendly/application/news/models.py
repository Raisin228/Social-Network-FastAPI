from application.core.model_types import id_pk
from database import Base
from sqlalchemy.orm import Mapped


class News(Base):
    __tablename__ = "news"

    id: Mapped[id_pk]
    # topic:
