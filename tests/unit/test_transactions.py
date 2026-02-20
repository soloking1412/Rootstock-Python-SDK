import threading
from unittest.mock import MagicMock

import pytest

from rootstock.constants import ChainId
from rootstock.exceptions import InsufficientFundsError
from rootstock.transactions import TransactionBuilder
from rootstock.wallet import Wallet

TEST_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
TEST_TO = "0x0000000000000000000000000000000000000001"


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.chain_id = ChainId.TESTNET
    provider.get_transaction_count.return_value = 5
    provider.get_gas_price.return_value = 60_000_000
    provider.estimate_gas.return_value = 21_000
    provider.get_balance.return_value = 10**18
    provider.send_raw_transaction.return_value = "0x" + "ab" * 32
    provider.wait_for_transaction.return_value = {
        "status": 1,
        "gasUsed": 21_000,
        "transactionHash": "0x" + "ab" * 32,
    }
    return provider


@pytest.fixture
def wallet():
    return Wallet.from_private_key(TEST_KEY, chain_id=ChainId.TESTNET)


@pytest.fixture
def builder(mock_provider, wallet):
    return TransactionBuilder(mock_provider, wallet)


class TestBuildTransaction:
    def test_basic_transfer(self, builder, mock_provider):
        tx = builder.build_transaction(to=TEST_TO, value=1000, gas_limit=21000)
        assert tx["to"].lower() == TEST_TO.lower()
        assert tx["value"] == 1000
        assert tx["gas"] == 21000
        assert tx["chainId"] == ChainId.TESTNET
        assert tx["nonce"] == 5
        assert tx["gasPrice"] == 60_000_000

    def test_auto_gas_estimation(self, builder, mock_provider):
        tx = builder.build_transaction(to=TEST_TO, value=0)
        mock_provider.estimate_gas.assert_called_once()
        assert tx["gas"] == 21_000

    def test_custom_nonce(self, builder):
        tx = builder.build_transaction(to=TEST_TO, nonce=99)
        assert tx["nonce"] == 99

    def test_custom_gas_price(self, builder):
        tx = builder.build_transaction(to=TEST_TO, gas_price=100_000_000, gas_limit=21000)
        assert tx["gasPrice"] == 100_000_000

    def test_no_eip1559_fields(self, builder):
        tx = builder.build_transaction(to=TEST_TO, gas_limit=21000)
        assert "maxFeePerGas" not in tx
        assert "maxPriorityFeePerGas" not in tx
        assert "type" not in tx

    def test_data_bytes(self, builder):
        tx = builder.build_transaction(to=TEST_TO, data=b"\xab\xcd", gas_limit=21000)
        assert tx["data"] == "0xabcd"

    def test_data_hex_string(self, builder):
        tx = builder.build_transaction(to=TEST_TO, data="0xabcd", gas_limit=21000)
        assert tx["data"] == "0xabcd"

    def test_empty_data(self, builder):
        tx = builder.build_transaction(to=TEST_TO, gas_limit=21000)
        assert tx["data"] == "0x"


class TestTransfer:
    def test_transfer_rbtc(self, builder, mock_provider):
        result = builder.transfer(to=TEST_TO, value_rbtc=0.001, wait=True)
        assert result["status"] == 1
        mock_provider.send_raw_transaction.assert_called_once()
        mock_provider.wait_for_transaction.assert_called_once()

    def test_transfer_wei(self, builder, mock_provider):
        result = builder.transfer(to=TEST_TO, value_wei=1000, wait=True)
        assert result["status"] == 1

    def test_transfer_no_wait(self, builder, mock_provider):
        result = builder.transfer(to=TEST_TO, value_wei=1000, wait=False)
        assert result == "0x" + "ab" * 32
        mock_provider.wait_for_transaction.assert_not_called()

    def test_transfer_zero_value(self, builder, mock_provider):
        result = builder.transfer(to=TEST_TO, wait=True)
        assert result["status"] == 1


class TestSignAndSend:
    def test_sign_and_send_wait(self, builder, mock_provider):
        tx = builder.build_transaction(to=TEST_TO, value=0, gas_limit=21000)
        result = builder.sign_and_send(tx, wait=True)
        assert result["status"] == 1

    def test_sign_and_send_no_wait(self, builder, mock_provider):
        tx = builder.build_transaction(to=TEST_TO, value=0, gas_limit=21000)
        result = builder.sign_and_send(tx, wait=False)
        assert isinstance(result, str)

    def test_insufficient_funds_raises(self, builder, mock_provider):
        mock_provider.get_balance.return_value = 100
        tx = builder.build_transaction(to=TEST_TO, value=10**18, gas_limit=21000)
        with pytest.raises(InsufficientFundsError):
            builder.sign_and_send(tx)


class TestEstimateTotalCost:
    def test_estimate(self, builder, mock_provider):
        cost = builder.estimate_total_cost(to=TEST_TO, value=10**18)
        assert "gas" in cost
        assert "gas_price" in cost
        assert "gas_cost" in cost
        assert "total_cost" in cost
        assert "total_cost_rbtc" in cost
        assert cost["gas"] == 21_000
        assert cost["gas_price"] == 60_000_000
        assert cost["gas_cost"] == 21_000 * 60_000_000
        assert cost["total_cost"] == 10**18 + 21_000 * 60_000_000

    def test_estimate_with_str_data(self, builder, mock_provider):
        cost = builder.estimate_total_cost(to=TEST_TO, value=0, data="0xabcd")
        assert "gas" in cost

    def test_estimate_with_bytes_data(self, builder, mock_provider):
        cost = builder.estimate_total_cost(to=TEST_TO, value=0, data=b"\xab\xcd")
        assert "gas" in cost


class TestNonceTracking:
    def test_nonce_offset_increments(self, mock_provider, wallet):
        builder = TransactionBuilder(mock_provider, wallet)
        mock_provider.get_transaction_count.return_value = 5
        n1 = builder._auto_nonce()
        assert n1 == 5
        n2 = builder._auto_nonce()
        assert n2 == 6
        n3 = builder._auto_nonce()
        assert n3 == 7

    def test_nonce_resets_when_base_changes(self, mock_provider, wallet):
        builder = TransactionBuilder(mock_provider, wallet)
        mock_provider.get_transaction_count.return_value = 5
        builder._auto_nonce()
        builder._auto_nonce()
        mock_provider.get_transaction_count.return_value = 7
        n = builder._auto_nonce()
        assert n == 7

    def test_reset_nonce(self, mock_provider, wallet):
        builder = TransactionBuilder(mock_provider, wallet)
        mock_provider.get_transaction_count.return_value = 5
        builder._auto_nonce()
        builder._auto_nonce()
        builder.reset_nonce()
        mock_provider.get_transaction_count.return_value = 5
        n = builder._auto_nonce()
        assert n == 5


class TestThreadSafety:
    def test_lock_exists(self, builder):
        assert hasattr(builder, "_lock")
        assert isinstance(builder._lock, type(threading.Lock()))
