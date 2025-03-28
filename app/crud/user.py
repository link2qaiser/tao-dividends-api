from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.models.auth import User
from app.schemas.auth import UserCreate


async def get_user(db: AsyncSession, user_id: int):
    """
    Get a user by ID
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str):
    """
    Get a user by username
    """
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    """
    Get a user by email
    """
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_username_or_email(db: AsyncSession, username_or_email: str):
    """
    Get a user by username or email
    """
    query = select(User).where(
        or_(User.username == username_or_email, User.email == username_or_email)
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Get multiple users with pagination
    """
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_user(db: AsyncSession, user: UserCreate):
    """
    Create a new user
    """
    hashed_password = User.get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Authenticate a user by username and password
    """
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not User.verify_password(password, user.hashed_password):
        return False
    return user
