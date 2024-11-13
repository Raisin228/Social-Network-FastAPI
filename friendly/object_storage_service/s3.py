from typing import Union

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
    async def get_client(cls) -> aiobotocore.session.AioBaseClient:
        """Создать клиента для взаимодействия с хранилищем"""
        config = {
            "region_name": settings.AWS_REGION_NAME,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "endpoint_url": settings.AWS_ENDPOINT_URL,
        }
        if cls.client is None:
            cls.session = cls.__get_session()
            cls.client = cls.session.create_client("s3", **config)
        return cls.client
