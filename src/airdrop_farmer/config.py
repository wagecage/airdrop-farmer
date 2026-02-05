"""
Configuration management for AirdropFarmer
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # Encryption
    MASTER_PASSWORD: str = os.getenv("MASTER_PASSWORD", "")

    # Notion API
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")

    # MegaETH Configuration
    MEGAETH_RPC_URL: str = os.getenv("MEGAETH_RPC_URL", "https://rpc.megaeth.testnet")
    MEGAETH_CHAIN_ID: int = int(os.getenv("MEGAETH_CHAIN_ID", "1234"))

    # Lighter DEX Configuration
    LIGHTER_API_URL: str = os.getenv("LIGHTER_API_URL", "https://api.lighter.xyz")
    LIGHTER_API_KEY: str = os.getenv("LIGHTER_API_KEY", "")

    # Polymarket Configuration
    POLYMARKET_API_URL: str = os.getenv("POLYMARKET_API_URL", "https://api.polymarket.com")
    POLYMARKET_API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")

    # Wallet Configuration
    NUM_WALLETS: int = int(os.getenv("NUM_WALLETS", "5"))
    WALLET_DERIVATION_PATH: str = os.getenv("WALLET_DERIVATION_PATH", "m/44'/60'/0'/0")

    # Scheduler Configuration
    RUN_INTERVAL_HOURS: int = int(os.getenv("RUN_INTERVAL_HOURS", "24"))
    ENABLE_CRON: bool = os.getenv("ENABLE_CRON", "true").lower() == "true"

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(DATA_DIR / "airdrop_farmer.db"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(LOGS_DIR / "airdrop_farmer.log"))

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        errors = []

        if not cls.MASTER_PASSWORD:
            errors.append("MASTER_PASSWORD is required")

        if not cls.NOTION_API_KEY:
            errors.append("NOTION_API_KEY is required")

        if not cls.NOTION_DATABASE_ID:
            errors.append("NOTION_DATABASE_ID is required")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

config = Config()
