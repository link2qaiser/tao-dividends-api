import logging
import json
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from app.core.config import settings
from app.services.cache import cache
from app.models.database import async_session
from app.crud.sentiment import create_sentiment_analysis

logger = logging.getLogger(__name__)


class SentimentService:
    """
    Service for analyzing tweet sentiment using Datura.ai and Chutes.ai
    """

    def __init__(self):
        self.datura_api_key = settings.DATURA_API_KEY
        self.chutes_api_key = settings.CHUTES_API_KEY
        self.cache_ttl = settings.CACHE_TTL

    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key for tweet search"""
        return f"tweets:{query}"

    def _generate_sentiment_cache_key(self, netuid: int) -> str:
        """Generate cache key for sentiment analysis"""
        return f"sentiment:netuid:{netuid}"

    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tweets using Datura.ai

        Args:
            query: Search query
            limit: Maximum number of tweets to return

        Returns:
            List of tweet data
        """
        logger.info(f"Searching tweets for query: {query}")

        # Check cache first
        cache_key = self._generate_cache_key(query)
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached tweets for query: {query}")
            return cached_result

        datura_endpoint = "https://api.datura.ai/v1/twitter/search"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    datura_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.datura_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"query": query, "limit": limit, "sort": "recent"},
                    timeout=30.0,
                )

                response.raise_for_status()
                result = response.json()

                if not result.get("data"):
                    logger.warning(f"No tweets found for query: {query}")
                    return []

                # Extract the actual tweet data
                tweets = result.get("data", [])

                # Cache the results
                await cache.set(cache_key, tweets, ttl=self.cache_ttl)

                logger.info(f"Found {len(tweets)} tweets for query: {query}")
                return tweets

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            # Provide mock data for development
            mock_tweets = [
                {
                    "id": "1234567890",
                    "text": f"This is a mock tweet about {query}. Very positive about this project!",
                    "created_at": "2023-06-15T14:30:00Z",
                    "user": {"username": "mock_user1", "name": "Mock User 1"},
                },
                {
                    "id": "0987654321",
                    "text": f"Another mock tweet about {query}. Not sure about the long-term viability.",
                    "created_at": "2023-06-15T14:35:00Z",
                    "user": {"username": "mock_user2", "name": "Mock User 2"},
                },
            ]
            return mock_tweets

    async def analyze_sentiment(self, tweets: List[Dict[str, Any]]) -> float:
        """
        Analyze sentiment of tweets using Chutes.ai

        Args:
            tweets: List of tweets to analyze

        Returns:
            Sentiment score from -100 (very negative) to +100 (very positive)
        """
        if not tweets:
            logger.warning("No tweets to analyze")
            return 0.0

        logger.info(f"Analyzing sentiment of {len(tweets)} tweets")

        # Extract text from tweets
        tweet_texts = [tweet.get("text", "") for tweet in tweets]

        # Format the prompt for sentiment analysis
        prompt = f"""
        Analyze the sentiment of the following tweets about Bittensor:
        
        {json.dumps(tweet_texts, indent=2)}
        
        Return a sentiment score from -100 (extremely negative) to +100 (extremely positive).
        Just return the numerical score.
        """

        # Use Chutes.ai API for sentiment analysis
        chutes_endpoint = "https://api.chutes.ai/v1/generate"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    chutes_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.chutes_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "chute_id": "20acffc0-0c5f-58e3-97af-21fc0b261ec4",  # Sentiment analysis chute
                        "prompt": prompt,
                        "max_tokens": 50,
                        "temperature": 0.0,  # Keep deterministic
                    },
                    timeout=60.0,
                )

                response.raise_for_status()
                result = response.json()

                # Extract the sentiment score from the response
                sentiment_text = result.get("text", "0").strip()
                try:
                    # Parse the sentiment score
                    sentiment_score = float(sentiment_text)

                    # Ensure the score is within the valid range
                    sentiment_score = max(-100.0, min(100.0, sentiment_score))

                    logger.info(
                        f"Sentiment analysis complete. Score: {sentiment_score}"
                    )
                    return sentiment_score

                except ValueError:
                    logger.error(f"Could not parse sentiment score: {sentiment_text}")
                    return 0.0

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")

            # Return a mock sentiment for development purposes
            # Calculate a simple mock sentiment based on tweet content
            positive_count = sum(
                1
                for text in tweet_texts
                if "positive" in text.lower() or "good" in text.lower()
            )
            negative_count = sum(
                1
                for text in tweet_texts
                if "negative" in text.lower() or "bad" in text.lower()
            )

            if positive_count > negative_count:
                return 75.0  # Mock positive sentiment
            elif negative_count > positive_count:
                return -75.0  # Mock negative sentiment
            else:
                return 0.0  # Mock neutral sentiment

    async def get_subnet_sentiment(self, netuid: int) -> Dict[str, Any]:
        """
        Get sentiment analysis for a subnet

        Args:
            netuid: Subnet ID

        Returns:
            Dictionary with sentiment score and related data
        """
        try:
            # Check cache first
            cache_key = self._generate_sentiment_cache_key(netuid)
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached sentiment for netuid {netuid}")
                return {**cached_result, "cached": True}

            # Construct search query
            query = f"Bittensor netuid {netuid}"

            # Search for tweets
            tweets = await self.search_tweets(query, limit=20)

            # If no tweets found, return neutral sentiment
            if not tweets:
                result = {
                    "netuid": netuid,
                    "sentiment_score": 0.0,
                    "tweet_count": 0,
                    "error": None,
                    "cached": False,
                }
                await cache.set(cache_key, result, ttl=self.cache_ttl)
                return result

            # Analyze sentiment of tweets
            sentiment_score = await self.analyze_sentiment(tweets)

            # Prepare result
            result = {
                "netuid": netuid,
                "sentiment_score": sentiment_score,
                "tweet_count": len(tweets),
                "error": None,
                "cached": False,
            }

            # Store in database
            async with async_session() as db:
                await create_sentiment_analysis(
                    db=db,
                    netuid=netuid,
                    sentiment_score=sentiment_score,
                    tweet_count=len(tweets),
                    data={
                        "tweets": [t.get("text", "") for t in tweets[:5]]
                    },  # Store first 5 tweets
                )

            # Cache the result
            await cache.set(cache_key, result, ttl=self.cache_ttl)

            return result

        except Exception as e:
            logger.error(f"Error getting subnet sentiment: {e}")
            return {
                "netuid": netuid,
                "sentiment_score": 0.0,
                "tweet_count": 0,
                "error": str(e),
                "cached": False,
            }


# Create singleton instance
sentiment_service = SentimentService()
