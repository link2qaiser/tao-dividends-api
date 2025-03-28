from app.worker import celery_app
from app.services.sentiment import sentiment_service
from app.services.blockchain import blockchain_service
from app.models.database import async_session
from app.crud.blockchain import create_transaction
import logging
import asyncio

logger = logging.getLogger(__name__)


@celery_app.task(name="process_sentiment_stake")
def process_sentiment_stake(netuid: int, hotkey: str):
    """
    Process sentiment analysis and stake/unstake accordingly

    Args:
        netuid: Subnet ID
        hotkey: Account ID or public key
    """
    logger.info(
        f"Processing sentiment-based stake for netuid {netuid}, hotkey {hotkey}"
    )

    # Use asyncio to handle async operations in Celery task
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_sentiment_stake(netuid, hotkey))


async def _process_sentiment_stake(netuid: int, hotkey: str):
    """
    Internal async implementation for sentiment-based staking
    """
    try:
        # Analyze sentiment for the subnet
        sentiment_result = await sentiment_service.get_subnet_sentiment(netuid)
        sentiment_score = sentiment_result.get("sentiment_score", 0.0)

        logger.info(f"Sentiment score for netuid {netuid}: {sentiment_score}")

        # Calculate stake amount: 0.01 TAO * sentiment score
        stake_amount = abs(0.01 * sentiment_score)

        # Skip if sentiment is neutral (zero) or stake amount is too small
        if sentiment_score == 0 or stake_amount < 0.01:
            logger.info(
                f"Skipping stake/unstake - sentiment score too low: {sentiment_score}"
            )
            return {
                "success": True,
                "message": "Skipped - sentiment too low",
                "sentiment_score": sentiment_score,
            }

        # Stake or unstake based on sentiment
        if sentiment_score > 0:
            # Positive sentiment - add stake
            result = await blockchain_service.add_stake(netuid, hotkey, stake_amount)
            transaction_type = "stake"
        else:
            # Negative sentiment - unstake
            result = await blockchain_service.unstake(netuid, hotkey, stake_amount)
            transaction_type = "unstake"

        # Record transaction in database
        async with async_session() as db:
            tx = await create_transaction(
                db=db,
                transaction_type=transaction_type,
                netuid=netuid,
                hotkey=hotkey,
                amount=stake_amount,
                transaction_hash=result.get("transaction_hash"),
                sentiment_score=sentiment_score,
                success=result.get("success", False),
                error=result.get("error"),
                transaction_data=result,  # Changed from 'metadata'
            )

        logger.info(
            f"Completed sentiment-based {transaction_type} for netuid {netuid}, hotkey {hotkey}"
        )
        return {
            "success": True,
            "transaction_type": transaction_type,
            "netuid": netuid,
            "hotkey": hotkey,
            "amount": stake_amount,
            "sentiment_score": sentiment_score,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error processing sentiment stake: {e}")
        return {"success": False, "error": str(e), "netuid": netuid, "hotkey": hotkey}
