from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.responses import BAD_REQUEST, REQUEST_ENTITY_TOO_LARGE
from application.storage.schemas import FileSavedOnCloud
from config import settings
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from object_storage_service.s3 import YOSService

router = APIRouter(prefix="/storage", tags=["File Storage"])


@router.post("/upload-file/", responses=REQUEST_ENTITY_TOO_LARGE | BAD_REQUEST, response_model=FileSavedOnCloud)
async def create_upload_file(file: UploadFile, user: User = Depends(get_current_user_access_token)):
    """Выгрузить файл на сервер. В ответ ссылка для доступа к файлу"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_FILE_TYPES:
        allow = list(map(lambda s: s.split("/")[-1], settings.ALLOWED_FILE_TYPES + settings.ALLOWED_IMAGE_TYPES))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The forbidden file type -> {file.content_type}. Easily download files in {allow}.",
        )

    if file.size > settings.FILE_MAX_SIZE_BYTE:
        converted_size = round(file.size / 1024**2, 2)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. The maximum allowed size 5MB. Current size -> {converted_size}MB.",
        )

    link_to_file = await YOSService.save_file(file.filename, user.id, file.file.read(), file.content_type)
    return FileSavedOnCloud(link_to_file=link_to_file)
