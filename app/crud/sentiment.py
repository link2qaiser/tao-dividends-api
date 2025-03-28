from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional

from app.models.sentiment import SentimentAnalysis


async def create_sentiment_analysis(
    db: AsyncSession,
    netuid: int,
    sentiment_score: float,
    tweet_count: int = 0,
    data: Optional[Dict[str, Any]] = None,
) -> SentimentAnalysis:
    """
    Create a new sentiment analysis record
    """
    sentiment = SentimentAnalysis(
        netuid=netuid,
        sentiment_score=sentiment_score,
        tweet_count=tweet_count,
        data=data,
    )

    db.add(sentiment)
    await db.commit()
    await db.refresh(sentiment)
    return sentiment


async def get_sentiment_analyses(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[SentimentAnalysis]:
    """
    Get sentiment analyses with pagination
    """
    query = (
        select(SentimentAnalysis)
        .order_by(SentimentAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_sentiment_analyses_for_netuid(
    db: AsyncSession, netuid: int, skip: int = 0, limit: int = 100
) -> List[SentimentAnalysis]:
    """
    Get sentiment analyses for a specific netuid
    """
    query = (
        select(SentimentAnalysis)
        .where(SentimentAnalysis.netuid == netuid)
        .order_by(SentimentAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_latest_sentiment_for_netuid(
    db: AsyncSession, netuid: int
) -> Optional[SentimentAnalysis]:
    """
    Get the latest sentiment analysis for a specific netuid
    """
    query = (
        select(SentimentAnalysis)
        .where(SentimentAnalysis.netuid == netuid)
        .order_by(SentimentAnalysis.created_at.desc())
        .limit(1)
    )

    result = await db.execute(query)
    return result.scalars().first()
