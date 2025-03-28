from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.auth import User
from app.services.sentiment import sentiment_service

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analyze")
async def analyze_sentiment(
    netuid: int = Query(..., description="Subnet ID to analyze"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually trigger sentiment analysis for a subnet

    Returns:
        Dictionary with sentiment score and related data
    """
    try:
        result = await sentiment_service.get_subnet_sentiment(netuid)
        return result
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sentiment: {str(e)}",
        )


@router.get("/tweets")
async def search_tweets(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of tweets to return"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search for tweets using Datura.ai

    Returns:
        Dictionary with tweet data
    """
    try:
        tweets = await sentiment_service.search_tweets(query, limit)
        return {"query": query, "tweets": tweets, "count": len(tweets)}
    except Exception as e:
        logger.error(f"Error searching tweets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search tweets: {str(e)}",
        )
