from typing import Union
from uuid import UUID

import aiobotocore.session
from config import settings


class YOSService:
    session: Union[aiobotocore.session.AioSession, None] = None
    client: Union[aiobotocore.session.AioBaseClient, None] = None

    @classmethod
    def __get_session(cls) -> aiobotocore.session.AioSession:
        """Создаёт сессию с Object Storage"""
        if cls.session is None:
            cls.session = aiobotocore.session.get_session()
        return cls.session

    @classmethod
    async def create_client(cls) -> aiobotocore.session.AioBaseClient:
        """Создать клиента для взаимодействия с хранилищем"""
        config = {
            "region_name": settings.AWS_REGION_NAME,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "endpoint_url": settings.AWS_ENDPOINT_URL,
        }
        if cls.client is None:
            cls.session = cls.__get_session()
            cls.client = await cls.session.create_client("s3", **config).__aenter__()
        return cls.client

    @classmethod
    async def save_file(cls, file_name: str, user_id: UUID, file: bytes, file_type: str) -> str:
        """Сохранить файл в облаке"""
        path_to_file = f"{user_id}/{file_name}"
        await cls.client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key=path_to_file, Body=file, ContentType=file_type)
        return f"{settings.AWS_ENDPOINT_URL}/{settings.AWS_BUCKET_NAME}/{path_to_file}"

    @classmethod
    async def remove_file(cls, usr_id: UUID, f_name: str) -> None:
        """Удалить файл с YOS"""
        path_to_file = f"{usr_id}/{f_name}"
        await cls.client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=path_to_file)

    @classmethod
    async def close_resources(cls) -> None:
        if cls.client is not None:
            await cls.client.__aexit__(None, None, None)
            cls.client = None
            cls.session = None

    @classmethod
    def convert_size(cls, size: int) -> float:
        """Переводит размер файла из Байт -> МБ"""
        return round(size / 1024**2, 2)


# TODO реализовать сжатие изображений (без потери качества)
# TODO добавить логи (писать в отдельный файл для S3)
