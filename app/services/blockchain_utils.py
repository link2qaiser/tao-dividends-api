"""
Utility functions for blockchain interactions

This module provides helper functions for common blockchain operations.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Union

import bittensor
from app.core.config import settings

logger = logging.getLogger(__name__)


async def create_wallet():
    """
    Create a Bittensor wallet from seed phrase
    """
    try:
        # Create wallet from seed
        wallet = bittensor.wallet(name="default_wallet", hotkey="default")
        success = wallet.regenerate(mnemonic=settings.WALLET_SEED)

        if not success:
            logger.error("Failed to regenerate wallet from seed")
            raise ValueError("Failed to regenerate wallet from seed")

        logger.info(f"Created wallet with coldkey: {wallet.coldkeypub.ss58_address}")
        return wallet
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise


async def connect_subtensor():
    """
    Connect to subtensor network
    """
    try:
        # Connect to the network specified in settings
        subtensor = bittensor.subtensor(
            chain_endpoint=settings.BITTENSOR_CHAIN_ENDPOINT,
            network=settings.BITTENSOR_NETWORK,
        )

        return subtensor
    except Exception as e:
        logger.error(f"Error connecting to subtensor: {e}")
        raise


async def get_balance(wallet):
    """
    Get wallet balance
    """
    try:
        subtensor = await connect_subtensor()
        balance = subtensor.get_balance(wallet.coldkeypub.ss58_address)
        return balance
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        raise
