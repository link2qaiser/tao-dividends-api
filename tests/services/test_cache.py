# tests/services/test_cache.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.services.cache import RedisCache


@pytest.mark.asyncio
async def test_get_client():
    """Test getting Redis client"""
    with patch("redis.asyncio.from_url", return_value=AsyncMock()) as mock_redis:
        cache = RedisCache()
        client = await cache.get_client()

        # Should call redis.asyncio.from_url
        mock_redis.assert_called_once()

        # Should cache the client
        client2 = await cache.get_client()
        assert client is client2  # Should return the same cached instance
        assert mock_redis.call_count == 1  # Should only create once


@pytest.mark.asyncio
async def test_get_set_delete():
    """Test get, set and delete operations"""
    # Mock Redis client
    mock_client = AsyncMock()
    mock_client.get.return_value = '{"key": "value"}'
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1

    with patch.object(RedisCache, "get_client", return_value=mock_client):
        cache = RedisCache()

        # Test get
        value = await cache.get("test_key")
        assert value == {"key": "value"}
        mock_client.get.assert_called_with("test_key")

        # Test set
        success = await cache.set("test_key", {"key": "value"}, ttl=60)
        assert success is True
        mock_client.set.assert_called_with("test_key", '{"key": "value"}', ex=60)

        # Test delete
        deleted = await cache.delete("test_key")
        assert deleted is True
        mock_client.delete.assert_called_with("test_key")


@pytest.mark.asyncio
async def test_keys():
    """Test keys operation"""
    # Mock Redis client
    mock_client = AsyncMock()
    mock_client.keys.return_value = ["key1", "key2"]

    with patch.object(RedisCache, "get_client", return_value=mock_client):
        cache = RedisCache()

        # Test keys
        keys = await cache.keys("test_*")
        assert keys == ["key1", "key2"]
        mock_client.keys.assert_called_with("test_*")
