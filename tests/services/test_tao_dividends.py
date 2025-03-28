# tests/api/test_tao_dividends.py
import pytest
from fastapi.testclient import TestClient


def test_get_tao_dividends_unauthorized(test_client):
    """Test getting tao dividends without authentication"""
    response = test_client.get("/api/v1/tao_dividends")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_get_tao_dividends(authorized_client, mock_blockchain_service):
    """Test getting tao dividends with authentication"""
    response = authorized_client.get("/api/v1/tao_dividends")
    assert response.status_code == 200

    data = response.json()
    assert "netuid" in data
    assert "hotkey" in data
    assert "dividend" in data
    assert "trade_triggered" in data
    assert data["trade_triggered"] is False


def test_get_tao_dividends_with_params(authorized_client, mock_blockchain_service):
    """Test getting tao dividends with specific netuid and hotkey"""
    response = authorized_client.get(
        "/api/v1/tao_dividends?netuid=18&hotkey=5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["netuid"] == 18
    assert data["hotkey"] == "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
    assert "dividend" in data


def test_get_tao_dividends_with_trade(
    authorized_client, mock_blockchain_service, monkeypatch
):
    """Test getting tao dividends with trade=true"""
    # Mock the celery task
    from app.tasks.stake import process_sentiment_stake

    # Create a mock task with delay method
    class MockTask:
        @staticmethod
        def delay(netuid, hotkey):
            return type("obj", (object,), {"id": "mock-task-id"})

    # Apply the mock
    monkeypatch.setattr(process_sentiment_stake, "delay", MockTask.delay)

    # Test the endpoint
    response = authorized_client.get("/api/v1/tao_dividends?trade=true")
    assert response.status_code == 200

    data = response.json()
    assert data["trade_triggered"] is True
    assert "task_id" in data
    assert data["task_id"] == "mock-task-id"
