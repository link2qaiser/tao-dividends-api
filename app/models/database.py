from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async engine with the string representation of the URL
database_url = str(settings.DATABASE_URL)
engine = create_async_engine(
    database_url,
    echo=True,  # Set to False in production
)

# Create async session
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create base model class
Base = declarative_base()


# Dependency to get DB session
async def get_db():
    """
    Dependency for getting async DB session
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
