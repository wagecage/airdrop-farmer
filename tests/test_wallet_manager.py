"""
Tests for wallet manager
"""
import pytest
import tempfile
import os
from pathlib import Path

from airdrop_farmer.wallet_manager import WalletManager
from airdrop_farmer.utils.encryption import Encryptor


@pytest.fixture
def encryptor():
    """Create test encryptor"""
    return Encryptor("test_password_123")


@pytest.fixture
def temp_storage():
    """Create temporary storage file"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


def test_create_wallet(encryptor, temp_storage):
    """Test wallet creation"""
    manager = WalletManager(encryptor, temp_storage)

    wallet = manager.create_wallet()

    assert wallet is not None
    assert wallet.address.startswith("0x")
    assert len(wallet.address) == 42


def test_create_multiple_wallets(encryptor, temp_storage):
    """Test creating multiple wallets"""
    manager = WalletManager(encryptor, temp_storage)

    wallets = manager.create_multiple_wallets(3)

    assert len(wallets) == 3
    addresses = [w.address for w in wallets]
    assert len(set(addresses)) == 3  # All unique


def test_wallet_persistence(encryptor, temp_storage):
    """Test wallet save and load"""
    # Create wallets
    manager1 = WalletManager(encryptor, temp_storage)
    original_wallets = manager1.create_multiple_wallets(2)
    original_addresses = [w.address for w in original_wallets]

    # Load wallets in new manager instance
    manager2 = WalletManager(encryptor, temp_storage)
    loaded_addresses = manager2.get_wallet_addresses()

    assert loaded_addresses == original_addresses


def test_get_wallet_by_address(encryptor, temp_storage):
    """Test retrieving wallet by address"""
    manager = WalletManager(encryptor, temp_storage)
    wallet = manager.create_wallet()

    retrieved = manager.get_wallet_by_address(wallet.address)

    assert retrieved is not None
    assert retrieved.address == wallet.address


def test_export_wallet_info(encryptor, temp_storage):
    """Test exporting wallet information"""
    manager = WalletManager(encryptor, temp_storage)
    manager.create_multiple_wallets(2)

    info = manager.export_wallet_info()

    assert len(info) == 2
    assert all("address" in i and "index" in i for i in info)
    assert all(i["address"].startswith("0x") for i in info)
