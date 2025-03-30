from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist
from application.core.responses import (
    BAD_REQUEST,
    CONFLICT,
    FORBIDDEN,
    NOT_FOUND,
    REQUEST_ENTITY_TOO_LARGE,
    UNAUTHORIZED,
)
from application.storage.dao import FileDao
from application.storage.schemas import FileRemoved, FileSavedOnCloud
from config import settings
from database import Transaction, get_async_session
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from object_storage_service.s3 import YOSService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/storage", tags=["File Storage"])


# TODO получить список своих файлов
@router.post(
    "/upload-file/",
    responses=REQUEST_ENTITY_TOO_LARGE | BAD_REQUEST | UNAUTHORIZED | FORBIDDEN | CONFLICT,
    response_model=FileSavedOnCloud,
)
async def create_upload_file(
    file: UploadFile,
    user: User = Depends(get_current_user_access_token),
):
    """Выгрузить файл на сервер. В ответ ссылка для доступа к файлу

    🟡**ATTENTION**🟡 Одинаковые файлы, загружаемые с одного аккаунта, будут заменять друг друга!
    """
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_FILE_TYPES:
        allow = list(
            map(
                lambda s: s.split("/")[-1],
                settings.ALLOWED_FILE_TYPES + settings.ALLOWED_IMAGE_TYPES,
            )
        )
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
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=prepared_str
        )

    link_to_file = await YOSService.save_file(
        file.filename, user.id, file.file.read(), file.content_type
    )
    async with Transaction() as session:
        record = await FileDao.add_record_about_new_file(user.id, file, link_to_file, session)
        data = record.to_dict()

    return FileSavedOnCloud(link_to_file=link_to_file, file_id=data["id"])


@router.delete(
    "/destroy-file/{file_name}",
    response_model=FileRemoved,
    responses=UNAUTHORIZED | FORBIDDEN | NOT_FOUND,
)
async def erase_file(
    file_name: str,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить файл по имени.

    Имя *ДОЛЖНО* содержать расширение -> (picture.png).

    Пользователь может удалять только свои файлы."""
    try:
        await FileDao.belongs_this_user(file_name, user, session)
        await YOSService.remove_file(user.id, file_name)
        res = (await FileDao.delete_by_filter(session, {"owner_id": user.id, "name": file_name}))[0]
        return FileRemoved(
            file_id=res[0], name=res[2], created_at=res[4], size=YOSService.convert_size(res[6])
        )
    except DataDoesNotExist as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{ex.msg} File with this name don't exist in the system (for current user).",
        )
