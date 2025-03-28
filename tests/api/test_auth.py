# tests/api/test_auth.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from app.models.auth import User


@pytest.mark.asyncio
async def test_register_user(test_client, db):
    """Test registering a new user"""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

    # Check that user was created in database
    query = select(func.count()).select_from(User).where(User.username == "testuser")
    result = await db.execute(query)
    count = result.scalar()
    assert count == 1


@pytest.mark.asyncio
async def test_login(test_client, db):
    """Test user login"""
    # First register a user
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200

    # Now try to login
    response = test_client.post(
        "/api/v1/auth/token",
        data={"username": "logintest", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(test_client, db):
    """Test login with wrong password"""
    # First register a user
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrongpwdtest",
            "email": "wrongpwd@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200

    # Now try to login with wrong password
    response = test_client.post(
        "/api/v1/auth/token",
        data={"username": "wrongpwdtest", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect username or password"
