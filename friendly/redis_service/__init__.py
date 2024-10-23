import pickle
from functools import wraps
from typing import Union

import redis.asyncio as async_redis
from application.auth.models import User
from config import settings
from fastapi import Request
from logger_config import filter_traceback, log
from redis import RedisError
from redis.asyncio import Redis


class RedisService:
    # TODO как будто 2 раза инициализируется async_client
    async_client: Redis = async_redis.from_url(settings.REDIS_URL)

    @classmethod
    async def connect_to(cls) -> None:
        cls.async_client = await async_redis.from_url(settings.REDIS_URL)

    @classmethod
    async def disconnect(cls) -> None:
        try:
            await cls.async_client.aclose()
        except AttributeError:
            print("There is no active connection")

    @classmethod
    def __key_builder(cls, request: Request, user: Union[User, None]) -> str:
        """Строитель ключей для noSQL базы"""
        full_path = request.url.path
        if request.query_params:
            sort_query_params = "&".join(f"{k}={v}" for k, v in sorted(request.query_params.items()))
            full_path += "?" + sort_query_params

        return full_path if user is None else f"{user.id}:{full_path}"

    @classmethod
    def cache_response(cls, ttl: int = 30, udc_pdc: bool = True):
        """Декоратор для кэширования ответов [ttl: Time to live in seconds]
        udc_pdc - user data cache or public data cache (данные для конкретного человека или одинаковые для всех)
        True - кэшируем данные только конкретного пользователя для него
        False - публичные часто запрашиваемые данные
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("_request", None)
                user: Union[User, None] = None
                if udc_pdc:
                    user = kwargs.get("user", None)
                cache_key = cls.__key_builder(request, user)

                cached_data_bytes = await cls.async_client.get(cache_key)
                if cached_data_bytes:
                    clean_data = pickle.loads(cached_data_bytes)
                    return clean_data

                response = await func(*args, **kwargs)
                bytes_data = pickle.dumps(response)
                try:
                    await cls.async_client.set(cache_key, bytes_data, ex=ttl)
                except RedisError as ex:
                    log.error("".join(filter_traceback(ex)))
                return response

            return wrapper

        return decorator
