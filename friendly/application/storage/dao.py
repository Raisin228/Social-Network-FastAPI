from typing import Dict
from uuid import UUID

from application.auth.models import User
from application.core.exceptions import DataDoesNotExist, InvalidAccessRights
from application.storage.models import File, FileType
from data_access_object.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession


class FileTypeDao(BaseDAO):
    model = FileType

    @classmethod
    async def get_type_id_file_content_type(cls, content_type: str, session: AsyncSession) -> Dict | None:
        cut_mime_type: str = content_type.split("/")[-1].upper()
        row = await FileTypeDao.find_by_filter(session, {"obj_type": cut_mime_type})
        return row.get("id")


class FileDao(BaseDAO):
    model = File

    @classmethod
    async def belongs_this_user(cls, file_id: UUID, usr: User, session: AsyncSession) -> bool:
        """Является ли пользователь создателем файла?"""
        file_record = await FileDao.find_by_filter(session, {"id": file_id})
        if file_record is None:
            raise DataDoesNotExist
        elif file_record.get("owner_id") != usr.id:
            raise InvalidAccessRights

        return True
