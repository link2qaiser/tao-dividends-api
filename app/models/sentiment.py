from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class SentimentAnalysis(Base):
    """
    Model for storing sentiment analysis results
    """

    __tablename__ = "sentiment_analyses"

    id = Column(Integer, primary_key=True, index=True)
    netuid = Column(Integer, nullable=False)
    tweet_count = Column(Integer, default=0)
    sentiment_score = Column(Float, nullable=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
