from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class BlockchainTransaction(Base):
    """
    Model for storing blockchain transaction history
    """

    __tablename__ = "blockchain_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String, nullable=False)
    netuid = Column(Integer, nullable=False)
    hotkey = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_hash = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error = Column(String, nullable=True)
    transaction_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
