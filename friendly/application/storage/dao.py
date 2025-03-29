from datetime import datetime, timezone
from typing import Dict
from uuid import UUID

from application.auth.models import User
from application.core.exceptions import DataDoesNotExist
from application.storage.models import File, FileType
from data_access_object.base import BaseDAO
from fastapi import UploadFile
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
    async def belongs_this_user(cls, f_name: str, usr: User, session: AsyncSession) -> bool:
        """Является ли пользователь создателем файла?"""
        file_record = await FileDao.find_by_filter(session, {"owner_id": usr.id, "name": f_name})
        if file_record is None:
            raise DataDoesNotExist
        return True

    @classmethod
    async def add_record_about_new_file(cls, u_id: UUID, file: UploadFile, link_to: str, session: AsyncSession) -> File:
        """Добавляет запись о новом файле (загружен в YOS)"""
        model_type = await FileTypeDao.get_type_id_file_content_type(file.content_type, session)

        search_param = {"owner_id": u_id, "name": file.filename, "s3_path": link_to}
        is_exist_row = await FileDao.find_by_filter(session, search_param)
        if is_exist_row is None:
            return await FileDao.add(
                session,
                {"owner_id": u_id, "name": file.filename, "s3_path": link_to, "type_id": model_type, "size": file.size},
            )
        temp = (
            await FileDao.update_row(
                session,
                {
                    "uploaded_at": datetime.now(timezone.utc).replace(tzinfo=None),
                    "type_id": model_type,
                    "size": file.size,
                },
                search_param,
            )
        )[0]
        return File(
            id=temp[0],
            owner_id=temp[1],
            name=temp[2],
            s3_path=temp[3],
            uploaded_at=temp[4],
            type_id=temp[5],
            size=temp[6],
        )
