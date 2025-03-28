from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional

from app.models.blockchain import BlockchainTransaction


async def create_transaction(
    db: AsyncSession,
    transaction_type: str,
    netuid: int,
    hotkey: str,
    amount: float,
    transaction_hash: Optional[str] = None,
    sentiment_score: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    transaction_data: Optional[Dict[str, Any]] = None,
) -> BlockchainTransaction:
    """
    Create a new blockchain transaction record
    """
    transaction = BlockchainTransaction(
        transaction_type=transaction_type,
        netuid=netuid,
        hotkey=hotkey,
        amount=amount,
        transaction_hash=transaction_hash,
        sentiment_score=sentiment_score,
        success=success,
        error=error,
        transaction_data=transaction_data,
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def get_transactions(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[BlockchainTransaction]:
    """
    Get blockchain transactions with pagination
    """
    query = (
        select(BlockchainTransaction)
        .order_by(BlockchainTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_transactions_for_hotkey(
    db: AsyncSession, hotkey: str, skip: int = 0, limit: int = 100
) -> List[BlockchainTransaction]:
    """
    Get blockchain transactions for a specific hotkey
    """
    query = (
        select(BlockchainTransaction)
        .where(BlockchainTransaction.hotkey == hotkey)
        .order_by(BlockchainTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_transactions_for_netuid(
    db: AsyncSession, netuid: int, skip: int = 0, limit: int = 100
) -> List[BlockchainTransaction]:
    """
    Get blockchain transactions for a specific netuid
    """
    query = (
        select(BlockchainTransaction)
        .where(BlockchainTransaction.netuid == netuid)
        .order_by(BlockchainTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()
