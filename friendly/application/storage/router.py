from uuid import UUID

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist, InvalidAccessRights
from application.core.responses import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_FOUND,
    REQUEST_ENTITY_TOO_LARGE,
    UNAUTHORIZED,
)
from application.storage.dao import FileDao, FileTypeDao
from application.storage.schemas import FileRemoved, FileSavedOnCloud
from config import settings
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from object_storage_service.s3 import YOSService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/storage", tags=["File Storage"])


@router.post(
    "/upload-file/",
    responses=REQUEST_ENTITY_TOO_LARGE | BAD_REQUEST | UNAUTHORIZED | FORBIDDEN,
    response_model=FileSavedOnCloud,
)
async def create_upload_file(
    file: UploadFile,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Выгрузить файл на сервер. В ответ ссылка для доступа к файлу"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_FILE_TYPES:
        allow = list(map(lambda s: s.split("/")[-1], settings.ALLOWED_FILE_TYPES + settings.ALLOWED_IMAGE_TYPES))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The forbidden file type -> {file.content_type}. Easily download files in {allow}.",
        )
    elif len(file.filename) > 32 or len(file.filename) < 6:
        prep_str = (
            f"The file name should be NO more than 32 and less than 6 characters long. Now -> "
            f"{len(file.filename)}sym."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=prep_str,
        )
    elif file.size > settings.FILE_MAX_SIZE_BYTE:
        tmp = f"File too large. The maximum allowed size {YOSService.convert_size(settings.FILE_MAX_SIZE_BYTE)}MB. "
        prepared_str = tmp + f"Current size -> {YOSService.convert_size(file.size)}MB."
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=prepared_str)

    link_to_file = await YOSService.save_file(file.filename, user.id, file.file.read(), file.content_type)
    model_type = await FileTypeDao.get_type_id_file_content_type(file.content_type, session)
    await FileDao.add_one(
        session,
        {"owner_id": user.id, "name": file.filename, "s3_path": link_to_file, "type_id": model_type, "size": file.size},
    )
    return FileSavedOnCloud(link_to_file=link_to_file)


@router.delete(
    "/destroy-file/{file_identity}", response_model=FileRemoved, responses=UNAUTHORIZED | FORBIDDEN | NOT_FOUND
)
async def erase_file(
    file_identity: UUID,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        await FileDao.belongs_this_user(file_identity, user, session)
        res = (await FileDao.delete_by_filter(session, {"id": file_identity}))[0]
        return FileRemoved(file_id=res[0], name=res[2], created_at=res[4], size=res[6])
    except DataDoesNotExist as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{ex.msg} File with this ID don't exist in the system.",
        )
    except InvalidAccessRights as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"{ex.msg} You cannot delete files from other users!"
        )
