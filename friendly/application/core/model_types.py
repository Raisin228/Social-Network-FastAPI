import uuid
from typing import Annotated

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import MappedColumn

id_pk = Annotated[
    uuid.UUID, MappedColumn(UUID(as_uuid=True), primary_key=True, insert_default=uuid.uuid4)
]
userId_fk = Annotated[
    uuid.UUID, MappedColumn(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
]
