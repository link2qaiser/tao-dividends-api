# tests/api/test_sentiment.py
import pytest
from fastapi.testclient import TestClient


def test_analyze_sentiment_unauthorized(test_client):
    """Test analyzing sentiment without authentication"""
    response = test_client.get("/api/v1/sentiment/analyze?netuid=18")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_analyze_sentiment(authorized_client, mock_sentiment_service):
    """Test analyzing sentiment with authentication"""
    response = authorized_client.get("/api/v1/sentiment/analyze?netuid=18")
    assert response.status_code == 200

    data = response.json()
    assert data["netuid"] == 18
    assert "sentiment_score" in data
    assert "tweet_count" in data
    assert data["error"] is None


def test_search_tweets_unauthorized(test_client):
    """Test searching tweets without authentication"""
    response = test_client.get("/api/v1/sentiment/tweets?query=Bittensor")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_search_tweets(authorized_client, mock_sentiment_service):
    """Test searching tweets with authentication"""
    response = authorized_client.get("/api/v1/sentiment/tweets?query=Bittensor")
    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "Bittensor"
    assert "tweets" in data
    assert "count" in data
    assert len(data["tweets"]) > 0
    assert data["count"] == len(data["tweets"])
