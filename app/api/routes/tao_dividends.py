from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.database import get_db
from app.models.auth import User
from app.services.blockchain import blockchain_service
from app.tasks.stake import process_sentiment_stake

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tao_dividends")
async def get_tao_dividends(
    netuid: Optional[int] = Query(None, description="Subnet ID"),
    hotkey: Optional[str] = Query(None, description="Account ID or public key"),
    trade: bool = Query(
        False, description="Whether to trigger stake/unstake based on sentiment"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Tao dividends data for a given subnet and hotkey.

    If netuid is omitted, returns data for all netuids.
    If hotkey is omitted, returns data for all hotkeys on the specified netuid.
    If trade is true, triggers a background task to analyze sentiment and stake/unstake accordingly.
    """
    # Use defaults if parameters not provided
    netuid = netuid if netuid is not None else settings.DEFAULT_NETUID
    hotkey = hotkey if hotkey is not None else settings.DEFAULT_HOTKEY

    try:
        # Query the blockchain for Tao dividends
        result = await blockchain_service.get_tao_dividends(
            netuid=netuid, hotkey=hotkey
        )

        # Add trade flag to result
        result["trade_triggered"] = trade

        # If trade is enabled, trigger sentiment analysis and stake/unstake
        if trade:
            logger.info(
                f"Trade is enabled. Triggering sentiment analysis for netuid {netuid}, hotkey {hotkey}"
            )

            # Trigger the Celery task for sentiment analysis and staking
            task = process_sentiment_stake.delay(netuid, hotkey)

            # Add task ID to result
            result["task_id"] = task.id
            logger.info(f"Sentiment analysis task triggered with ID: {task.id}")

        return result

    except Exception as e:
        logger.error(f"Error retrieving Tao dividends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Tao dividends: {str(e)}",
        )
