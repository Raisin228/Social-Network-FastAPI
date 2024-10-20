import redis.asyncio as async_redis
from config import settings
from redis.asyncio import Redis


class RedisService:
    async_client: Redis

    @classmethod
    async def connect_to(cls) -> None:
        cls.async_client = await async_redis.from_url(settings.REDIS_URL)

    @classmethod
    async def disconnect(cls) -> None:
        try:
            await cls.async_client.aclose()
        except AttributeError:
            print("There is no active connection")

    # @classmethod
    # async def add_k(cls):
    #     await cls.async_client.set('abc', 123)
    #
    # @classmethod
    # async def del_k(cls):
    #     await cls.async_client.delete('abc')
