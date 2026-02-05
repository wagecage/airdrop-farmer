"""
Wallet management system with secure storage
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3

from .utils.encryption import Encryptor
from .utils.logger import setup_logger
from .config import config

logger = setup_logger()


class WalletManager:
    """Manage cryptocurrency wallets with encrypted storage"""

    def __init__(self, encryptor: Encryptor, storage_path: Optional[str] = None):
        """
        Initialize wallet manager

        Args:
            encryptor: Encryptor instance for secure storage
            storage_path: Path to store encrypted wallet data
        """
        self.encryptor = encryptor
        self.storage_path = Path(storage_path or config.DATA_DIR / "wallets.enc")
        self.wallets: List[LocalAccount] = []
        self._load_wallets()

    def create_wallet(self) -> LocalAccount:
        """
        Create a new wallet

        Returns:
            New wallet account
        """
        Account.enable_unaudited_hdwallet_features()
        account = Account.create()
        self.wallets.append(account)
        logger.info(f"Created new wallet: {account.address}")
        return account

    def create_multiple_wallets(self, count: int) -> List[LocalAccount]:
        """
        Create multiple wallets

        Args:
            count: Number of wallets to create

        Returns:
            List of created wallets
        """
        new_wallets = []
        for i in range(count):
            wallet = self.create_wallet()
            new_wallets.append(wallet)
            logger.info(f"Created wallet {i+1}/{count}: {wallet.address}")

        self._save_wallets()
        return new_wallets

    def get_wallets(self) -> List[LocalAccount]:
        """
        Get all managed wallets

        Returns:
            List of wallet accounts
        """
        return self.wallets

    def get_wallet_addresses(self) -> List[str]:
        """
        Get all wallet addresses

        Returns:
            List of wallet addresses
        """
        return [wallet.address for wallet in self.wallets]

    def get_wallet_by_address(self, address: str) -> Optional[LocalAccount]:
        """
        Get wallet by address

        Args:
            address: Wallet address

        Returns:
            Wallet account or None
        """
        for wallet in self.wallets:
            if wallet.address.lower() == address.lower():
                return wallet
        return None

    def _save_wallets(self) -> None:
        """Save wallets to encrypted storage"""
        wallet_data = []
        for wallet in self.wallets:
            wallet_data.append({
                "address": wallet.address,
                "private_key": wallet.key.hex()
            })

        json_data = json.dumps(wallet_data)
        encrypted_data = self.encryptor.encrypt(json_data)

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            f.write(encrypted_data)

        logger.info(f"Saved {len(self.wallets)} wallets to encrypted storage")

    def _load_wallets(self) -> None:
        """Load wallets from encrypted storage"""
        if not self.storage_path.exists():
            logger.info("No existing wallet storage found")
            return

        try:
            with open(self.storage_path, 'r') as f:
                encrypted_data = f.read()

            json_data = self.encryptor.decrypt(encrypted_data)
            wallet_data = json.loads(json_data)

            self.wallets = []
            for data in wallet_data:
                account = Account.from_key(data["private_key"])
                self.wallets.append(account)

            logger.info(f"Loaded {len(self.wallets)} wallets from encrypted storage")

        except Exception as e:
            logger.error(f"Failed to load wallets: {e}")
            raise

    def export_wallet_info(self) -> List[Dict[str, str]]:
        """
        Export wallet information (addresses only, for logging)

        Returns:
            List of wallet info dictionaries
        """
        return [
            {
                "address": wallet.address,
                "index": i
            }
            for i, wallet in enumerate(self.wallets)
        ]

    def get_wallet_balance(self, address: str, web3: Web3) -> int:
        """
        Get wallet balance

        Args:
            address: Wallet address
            web3: Web3 instance

        Returns:
            Balance in wei
        """
        try:
            balance = web3.eth.get_balance(address)
            return balance
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return 0

    def sign_transaction(self, wallet: LocalAccount, transaction: dict) -> dict:
        """
        Sign a transaction

        Args:
            wallet: Wallet account
            transaction: Transaction dictionary

        Returns:
            Signed transaction
        """
        signed = wallet.sign_transaction(transaction)
        return signed
