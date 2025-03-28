import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from decimal import Decimal
import time

import bittensor
from app.services.cache import cache
from app.core.config import settings
from bittensor.utils.balance import Balance

logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service for interacting with the Bittensor blockchain
    """

    def __init__(self):
        self._async_subtensor = None
        self._wallet = None
        self._cache_ttl = settings.CACHE_TTL

    async def get_async_subtensor(self):
        """
        Get or create AsyncSubtensor instance (mock implementation)
        """
        if self._async_subtensor is None:
            # Create a mock implementation for development
            class MockAsyncSubtensor:
                async def connect(self):
                    return True

                async def get_tao_dividend_for_subnet(self, hotkey, netuid):
                    return 123456789.0

                async def neurons_for_subnet(self, netuid):
                    class MockNeuron:
                        def __init__(self, hotkey):
                            self.hotkey = hotkey

                    return [
                        MockNeuron("5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"),
                        MockNeuron("5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"),
                    ]

                # Add other required methods

            self._async_subtensor = MockAsyncSubtensor()
            logger.info("Using mock AsyncSubtensor implementation")

        return self._async_subtensor

    async def get_wallet(self):
        """
        Get or create wallet instance
        """
        if self._wallet is None:
            try:
                # Create wallet from seed phrase
                logger.info("Creating wallet from seed phrase")
                self._wallet = bittensor.wallet(name="default", hotkey="default")

                # Regenerate from mnemonic
                success = self._wallet.regenerate(mnemonic=settings.WALLET_SEED)
                if not success:
                    logger.error("Failed to regenerate wallet from seed")
                    raise ValueError("Failed to regenerate wallet from seed phrase")

                logger.info(
                    f"Successfully created wallet with coldkey: {self._wallet.coldkeypub.ss58_address}"
                )
                logger.info(f"Hotkey: {self._wallet.hotkey.ss58_address}")
            except Exception as e:
                logger.error(f"Error creating wallet: {e}")
                raise

        return self._wallet

    def _generate_cache_key(self, netuid: Optional[int], hotkey: Optional[str]) -> str:
        """
        Generate cache key for tao dividends query
        """
        return f"tao_dividends:{netuid or 'all'}:{hotkey or 'all'}"

    async def get_tao_dividends(
        self, netuid: Optional[int] = None, hotkey: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Tao dividends for a subnet and hotkey

        If netuid is None, returns data for all netuids
        If hotkey is None, returns data for all hotkeys on the specified netuid

        Returns cached results if available
        """
        cache_key = self._generate_cache_key(netuid, hotkey)

        # Try to get from cache first
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached Tao dividends for {cache_key}")
            return {**cached_result, "cached": True}

        try:
            # Get AsyncSubtensor instance
            subtensor = await self.get_async_subtensor()

            start_time = time.time()
            result = {}

            # Case 1: Both netuid and hotkey are specified
            if netuid is not None and hotkey is not None:
                logger.info(
                    f"Querying Tao dividends for netuid {netuid}, hotkey {hotkey}"
                )

                # Query the blockchain for Tao dividends
                # Convert dividend to float for JSON serialization
                dividend = await subtensor.get_tao_dividend_for_subnet(
                    hotkey=hotkey, netuid=netuid
                )

                # Format the result
                result = {
                    "netuid": netuid,
                    "hotkey": hotkey,
                    "dividend": float(dividend) if dividend is not None else 0.0,
                    "cached": False,
                }

            # Case 2: Only netuid is specified
            elif netuid is not None:
                logger.info(
                    f"Querying Tao dividends for all hotkeys on netuid {netuid}"
                )

                # Get all hotkeys for the subnet
                try:
                    neuron_data = await subtensor.neurons_for_subnet(netuid=netuid)

                    # Extract hotkeys and query dividends for each
                    hotkeys_data = []
                    for neuron in neuron_data:
                        hotkey_address = neuron.hotkey
                        dividend = await subtensor.get_tao_dividend_for_subnet(
                            hotkey=hotkey_address, netuid=netuid
                        )

                        # Get stake for this hotkey in the subnet
                        stake = await subtensor.get_stake_for_hotkey_and_subnet(
                            hotkey=hotkey_address, netuid=netuid
                        )

                        hotkeys_data.append(
                            {
                                "hotkey": hotkey_address,
                                "dividend": (
                                    float(dividend) if dividend is not None else 0.0
                                ),
                                "stake": float(stake) if stake is not None else 0.0,
                            }
                        )

                    result = {
                        "netuid": netuid,
                        "hotkeys": hotkeys_data,
                        "cached": False,
                    }
                except Exception as subnet_error:
                    logger.error(
                        f"Error querying neurons for subnet {netuid}: {subnet_error}"
                    )
                    result = {
                        "netuid": netuid,
                        "error": f"Failed to query neurons: {str(subnet_error)}",
                        "cached": False,
                    }

            # Case 3: Only hotkey is specified
            elif hotkey is not None:
                logger.info(
                    f"Querying Tao dividends for hotkey {hotkey} on all subnets"
                )

                # Get all subnets
                try:
                    subnet_list = await subtensor.get_all_subnet_netuids()

                    # Query dividends for each subnet
                    subnet_data = []
                    for subnet_id in subnet_list:
                        try:
                            dividend = await subtensor.get_tao_dividend_for_subnet(
                                hotkey=hotkey, netuid=subnet_id
                            )

                            subnet_data.append(
                                {
                                    "netuid": subnet_id,
                                    "dividend": (
                                        float(dividend) if dividend is not None else 0.0
                                    ),
                                }
                            )
                        except Exception as subnet_error:
                            logger.warning(
                                f"Error querying dividend for subnet {subnet_id}: {subnet_error}"
                            )
                            # Skip failed subnets but continue
                            continue

                    result = {"hotkey": hotkey, "netuids": subnet_data, "cached": False}
                except Exception as e:
                    logger.error(f"Error querying subnet list: {e}")
                    result = {
                        "hotkey": hotkey,
                        "error": f"Failed to query subnets: {str(e)}",
                        "cached": False,
                    }

            # Case 4: Neither netuid nor hotkey is specified
            else:
                logger.info("Querying Tao dividends for all subnets")

                # Get all subnets
                try:
                    subnet_list = await subtensor.get_all_subnet_netuids()

                    # Limit to a few subnets to avoid excessive queries
                    subnet_list = subnet_list[:5]

                    # Query data for each subnet
                    subnet_data = []
                    for subnet_id in subnet_list:
                        try:
                            # Get sample of neurons (limit to 5 per subnet)
                            neurons = await subtensor.neurons_for_subnet(
                                netuid=subnet_id
                            )
                            neurons = neurons[
                                :5
                            ]  # Limit to 5 neurons for large subnets

                            hotkeys_data = []
                            for neuron in neurons:
                                hotkey_address = neuron.hotkey
                                dividend = await subtensor.get_tao_dividend_for_subnet(
                                    hotkey=hotkey_address, netuid=subnet_id
                                )

                                stake = await subtensor.get_stake_for_hotkey_and_subnet(
                                    hotkey=hotkey_address, netuid=subnet_id
                                )

                                hotkeys_data.append(
                                    {
                                        "hotkey": hotkey_address,
                                        "dividend": (
                                            float(dividend)
                                            if dividend is not None
                                            else 0.0
                                        ),
                                        "stake": (
                                            float(stake) if stake is not None else 0.0
                                        ),
                                    }
                                )

                            subnet_data.append(
                                {"netuid": subnet_id, "hotkeys": hotkeys_data}
                            )
                        except Exception as subnet_error:
                            logger.warning(
                                f"Error querying data for subnet {subnet_id}: {subnet_error}"
                            )
                            # Skip failed subnets but continue
                            continue

                    result = {"subnets": subnet_data, "cached": False}
                except Exception as e:
                    logger.error(f"Error querying subnet list: {e}")
                    result = {
                        "error": f"Failed to query subnets: {str(e)}",
                        "cached": False,
                    }

            end_time = time.time()
            logger.info(
                f"Blockchain query completed in {end_time - start_time:.2f} seconds"
            )

            # Cache the result
            await cache.set(cache_key, result, ttl=self._cache_ttl)

            return result

        except Exception as e:
            logger.error(f"Error retrieving Tao dividends: {e}")

            # Return error response
            error_result = {
                "error": f"Failed to retrieve Tao dividends: {str(e)}",
                "cached": False,
            }

            if netuid is not None:
                error_result["netuid"] = netuid
            if hotkey is not None:
                error_result["hotkey"] = hotkey

            return error_result

    async def add_stake(
        self, netuid: int, hotkey: str, amount: float
    ) -> Dict[str, Any]:
        """
        Add stake to a hotkey on a subnet

        Args:
            netuid: Subnet ID
            hotkey: Account ID or public key
            amount: Amount of TAO to stake

        Returns:
            Dictionary with transaction result
        """
        logger.info(f"Adding stake to hotkey {hotkey} on subnet {netuid}: {amount} TAO")

        try:
            # Get AsyncSubtensor and wallet
            subtensor = await self.get_async_subtensor()
            wallet = await self.get_wallet()

            # Convert amount to Balance
            stake_amount = bittensor.Balance.from_float(amount)

            # Check wallet balance
            balance = await subtensor.get_balance(wallet.coldkeypub.ss58_address)
            logger.info(f"Wallet balance: {balance}")

            if balance < stake_amount:
                logger.error(f"Insufficient balance: {balance} < {stake_amount}")
                return {
                    "success": False,
                    "netuid": netuid,
                    "hotkey": hotkey,
                    "amount": amount,
                    "error": f"Insufficient balance: {balance} < {stake_amount}",
                }

            # Add stake
            logger.info(
                f"Submitting add_stake extrinsic: {netuid}, {hotkey}, {stake_amount}"
            )

            # Submit the extrinsic with wallet signature
            tx_hash = await subtensor.add_stake(
                wallet=wallet,
                hotkey_ss58=hotkey,
                amount=stake_amount,
                wait_for_inclusion=True,
                wait_for_finalization=False,  # Don't wait for finalization for faster response
            )

            logger.info(f"add_stake extrinsic submitted successfully: {tx_hash}")

            return {
                "success": True,
                "netuid": netuid,
                "hotkey": hotkey,
                "amount": amount,
                "transaction_hash": str(tx_hash),
            }

        except Exception as e:
            logger.error(f"Error adding stake: {e}")
            return {
                "success": False,
                "netuid": netuid,
                "hotkey": hotkey,
                "amount": amount,
                "error": str(e),
            }

    async def unstake(self, netuid: int, hotkey: str, amount: float) -> Dict[str, Any]:
        """
        Unstake TAO from a hotkey on a subnet

        Args:
            netuid: Subnet ID
            hotkey: Account ID or public key
            amount: Amount of TAO to unstake

        Returns:
            Dictionary with transaction result
        """
        logger.info(f"Unstaking from hotkey {hotkey} on subnet {netuid}: {amount} TAO")

        try:
            # Get AsyncSubtensor and wallet
            subtensor = await self.get_async_subtensor()
            wallet = await self.get_wallet()

            # Convert amount to Balance
            unstake_amount = bittensor.Balance.from_float(amount)

            # Check current stake
            current_stake = await subtensor.get_stake_for_hotkey_and_subnet(
                hotkey=hotkey, netuid=netuid
            )

            logger.info(f"Current stake: {current_stake}")

            if current_stake < unstake_amount:
                logger.error(f"Insufficient stake: {current_stake} < {unstake_amount}")
                return {
                    "success": False,
                    "netuid": netuid,
                    "hotkey": hotkey,
                    "amount": amount,
                    "error": f"Insufficient stake: {current_stake} < {unstake_amount}",
                }

            # Submit unstake extrinsic
            logger.info(
                f"Submitting unstake extrinsic: {netuid}, {hotkey}, {unstake_amount}"
            )

            tx_hash = await subtensor.unstake(
                wallet=wallet,
                hotkey_ss58=hotkey,
                amount=unstake_amount,
                wait_for_inclusion=True,
                wait_for_finalization=False,  # Don't wait for finalization for faster response
            )

            logger.info(f"unstake extrinsic submitted successfully: {tx_hash}")

            return {
                "success": True,
                "netuid": netuid,
                "hotkey": hotkey,
                "amount": amount,
                "transaction_hash": str(tx_hash),
            }

        except Exception as e:
            logger.error(f"Error unstaking: {e}")
            return {
                "success": False,
                "netuid": netuid,
                "hotkey": hotkey,
                "amount": amount,
                "error": str(e),
            }

    async def get_balance(self, wallet=None):
        """
        Get wallet balance
        """
        try:
            # Get AsyncSubtensor and wallet
            subtensor = await self.get_async_subtensor()

            if wallet is None:
                wallet = await self.get_wallet()

            # Get balance
            balance = await subtensor.get_balance(wallet.coldkeypub.ss58_address)

            return float(balance)

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise


# Create singleton instance
blockchain_service = BlockchainService()
