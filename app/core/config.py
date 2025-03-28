import os
from typing import Optional, Union, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator


class Settings(BaseSettings):
    API_TOKEN: str = "default_token_for_development"
    DATABASE_URL: PostgresDsn = (
        "postgresql+asyncpg://postgres:postgres@db:5432/tao_dividends"
    )
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT Settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: Union[int, str, None] = 30

    # Cache settings
    CACHE_TTL: Union[int, str, None] = 120

    # Bittensor settings
    BITTENSOR_CHAIN_ENDPOINT: str = "ws://127.0.0.1:9944"
    BITTENSOR_NETWORK: str = "testnet"
    DEFAULT_NETUID: Union[int, str, None] = 18
    DEFAULT_HOTKEY: str = ""

    # API keys
    DATURA_API_KEY: str = ""
    CHUTES_API_KEY: str = ""

    # Wallet seed for testnet
    WALLET_SEED: str = (
        "diamond like interest affair safe clarify lawsuit innocent beef van grief color"
    )

    # Database configuration (these will be ignored from environment)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def parse_access_token_expire(cls, v: Any) -> int:
        if v is None or v == "":
            return 30
        if isinstance(v, int):
            return v
        try:
            return int(v)
        except ValueError:
            return 30

    @field_validator("CACHE_TTL")
    @classmethod
    def parse_cache_ttl(cls, v: Any) -> int:
        if v is None or v == "":
            return 120
        if isinstance(v, int):
            return v
        try:
            return int(v)
        except ValueError:
            return 120

    @field_validator("DEFAULT_NETUID")
    @classmethod
    def parse_default_netuid(cls, v: Any) -> int:
        if v is None or v == "":
            return 18
        if isinstance(v, int):
            return v
        try:
            return int(v)
        except ValueError:
            return 18

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
