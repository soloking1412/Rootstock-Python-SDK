import pytest

from rootstock.constants import ChainId
from rootstock.wallet import Wallet

TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


@pytest.fixture
def test_wallet():
    return Wallet.from_private_key(TEST_PRIVATE_KEY, chain_id=ChainId.TESTNET)
