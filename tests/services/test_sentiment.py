# tests/services/test_sentiment.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.services.sentiment import SentimentService


@pytest.mark.asyncio
async def test_search_tweets():
    """Test searching tweets"""
    # Mock httpx client
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "1234567890",
                    "text": "This is a test tweet about Bittensor. Very positive!",
                    "created_at": "2023-06-15T14:30:00Z",
                    "user": {"username": "test_user1", "name": "Test User 1"},
                }
            ]
        }
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        # Test the function
        service = SentimentService()
        tweets = await service.search_tweets("Bittensor netuid 18", 1)

        assert len(tweets) == 1
        assert tweets[0]["id"] == "1234567890"
        assert "Bittensor" in tweets[0]["text"]


@pytest.mark.asyncio
async def test_analyze_sentiment():
    """Test analyzing sentiment of tweets"""
    # Mock tweets
    tweets = [
        {
            "id": "1234567890",
            "text": "This is a test tweet about Bittensor. Very positive!",
            "created_at": "2023-06-15T14:30:00Z",
            "user": {"username": "test_user1", "name": "Test User 1"},
        }
    ]

    # Mock httpx client
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json.return_value = {"text": "75.0"}
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        # Test the function
        service = SentimentService()
        sentiment_score = await service.analyze_sentiment(tweets)

        assert sentiment_score == 75.0


@pytest.mark.asyncio
async def test_get_subnet_sentiment(mock_sentiment_service):
    """Test getting sentiment for a subnet"""
    result = await mock_sentiment_service.get_subnet_sentiment(18)

    assert result["netuid"] == 18
    assert "sentiment_score" in result
    assert "tweet_count" in result
    assert result["error"] is None
