import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Optional


class RedisCache:
    """
    Redis cache service for storing and retrieving data
    """

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.ttl = settings.CACHE_TTL
        self.redis_client = None

    async def get_client(self):
        """
        Get or create Redis client
        """
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
        return self.redis_client

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        client = await self.get_client()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with TTL
        """
        client = await self.get_client()
        serialized_value = json.dumps(value)
        return await client.set(key, serialized_value, ex=ttl or self.ttl)

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        """
        client = await self.get_client()
        return await client.delete(key) > 0

    async def keys(self, pattern: str) -> list:
        """
        Get keys matching pattern
        """
        client = await self.get_client()
        return await client.keys(pattern)


# Create singleton instance
cache = RedisCache()
