from unittest.mock import MagicMock, patch

import pytest

from rootstock.constants import ChainId
from rootstock.exceptions import (
    GasEstimationError,
    NonceTooLowError,
    ProviderConnectionError,
    RPCError,
    TransactionRevertedError,
)
from rootstock.network import NetworkConfig
from rootstock.provider import RootstockProvider


@pytest.fixture
def mock_web3():
    with patch("rootstock.provider.Web3") as mock_web3_cls:
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.chain_id = 31
        mock_w3.eth.gas_price = 60_000_000
        mock_w3.eth.block_number = 5_000_000
        mock_w3.eth.get_balance.return_value = 10**18
        mock_w3.eth.get_transaction_count.return_value = 5
        mock_w3.middleware_onion = MagicMock()
        mock_web3_cls.return_value = mock_w3
        mock_web3_cls.HTTPProvider = MagicMock()
        mock_web3_cls.to_checksum_address = lambda addr: addr
        yield mock_w3


class TestProviderConstruction:
    def test_from_mainnet(self, mock_web3):
        provider = RootstockProvider.from_mainnet()
        assert provider.chain_id == ChainId.MAINNET
        assert provider.network.name == "Rootstock Mainnet"

    def test_from_testnet(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        assert provider.chain_id == ChainId.TESTNET
        assert provider.network.name == "Rootstock Testnet"

    def test_from_url(self, mock_web3):
        provider = RootstockProvider.from_url("http://localhost:4444", chain_id=33)
        assert provider.chain_id == 33

    def test_custom_rpc_url(self, mock_web3):
        provider = RootstockProvider.from_mainnet(rpc_url="https://custom.rpc.co")
        assert provider.network.rpc_url == "https://custom.rpc.co"

    def test_from_websocket(self, mock_web3):
        with patch("rootstock.provider.WebSocketProvider", create=True):
            provider = RootstockProvider.from_websocket("wss://node.example.com", chain_id=30)
            assert provider.chain_id == 30

    def test_is_connected(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        assert provider.is_connected is True

    def test_is_connected_false(self, mock_web3):
        mock_web3.is_connected.return_value = False
        provider = RootstockProvider.from_testnet()
        assert provider.is_connected is False

    def test_w3_property(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        assert provider.w3 is mock_web3

    def test_network_property(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        assert isinstance(provider.network, NetworkConfig)

    def test_max_retries_param(self, mock_web3):
        provider = RootstockProvider.from_testnet(max_retries=5)
        assert provider._max_retries == 5


class TestProviderReadMethods:
    def test_get_balance(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        balance = provider.get_balance("0x0000000000000000000000000000000000000001")
        assert balance == 10**18

    def test_get_transaction_count(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        nonce = provider.get_transaction_count("0x0000000000000000000000000000000000000001")
        assert nonce == 5

    def test_get_block_number(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        assert provider.get_block_number() == 5_000_000

    def test_get_gas_price(self, mock_web3):
        provider = RootstockProvider.from_testnet()
        assert provider.get_gas_price() == 60_000_000

    def test_get_block(self, mock_web3):
        mock_web3.eth.get_block.return_value = {"number": 100, "hash": "0xabc"}
        provider = RootstockProvider.from_testnet()
        block = provider.get_block(100)
        assert block["number"] == 100

    def test_get_transaction(self, mock_web3):
        mock_web3.eth.get_transaction.return_value = {"hash": "0xabc", "nonce": 0}
        provider = RootstockProvider.from_testnet()
        tx = provider.get_transaction("0xabc")
        assert tx["hash"] == "0xabc"

    def test_get_transaction_receipt(self, mock_web3):
        mock_web3.eth.get_transaction_receipt.return_value = {"status": 1, "gasUsed": 21000}
        provider = RootstockProvider.from_testnet()
        receipt = provider.get_transaction_receipt("0xabc")
        assert receipt["status"] == 1

    def test_get_code(self, mock_web3):
        mock_web3.eth.get_code.return_value = b"\x60\x80"
        provider = RootstockProvider.from_testnet()
        code = provider.get_code("0x0000000000000000000000000000000000000001")
        assert code == b"\x60\x80"

    def test_estimate_gas(self, mock_web3):
        mock_web3.eth.estimate_gas.return_value = 21000
        provider = RootstockProvider.from_testnet()
        gas = provider.estimate_gas({"to": "0x0000000000000000000000000000000000000001"})
        assert gas == 21000


class TestProviderWriteMethods:
    def test_send_raw_transaction(self, mock_web3):
        mock_web3.eth.send_raw_transaction.return_value = b"\xab" * 32
        provider = RootstockProvider.from_testnet()
        tx_hash = provider.send_raw_transaction(b"\x00")
        assert isinstance(tx_hash, str)

    def test_wait_for_transaction_success(self, mock_web3):
        mock_web3.eth.wait_for_transaction_receipt.return_value = {
            "status": 1,
            "gasUsed": 21000,
            "transactionHash": b"\xab" * 32,
        }
        provider = RootstockProvider.from_testnet()
        receipt = provider.wait_for_transaction("0x" + "ab" * 32)
        assert receipt["status"] == 1

    def test_wait_for_transaction_reverted(self, mock_web3):
        mock_web3.eth.wait_for_transaction_receipt.return_value = {
            "status": 0,
            "gasUsed": 21000,
            "transactionHash": b"\xab" * 32,
        }
        provider = RootstockProvider.from_testnet()
        with pytest.raises(TransactionRevertedError) as exc_info:
            provider.wait_for_transaction("0x" + "ab" * 32)
        assert exc_info.value.tx_hash == "0x" + "ab" * 32


class TestProviderErrorHandling:
    def test_estimate_gas_contract_logic_error(self, mock_web3):
        from web3.exceptions import ContractLogicError

        mock_web3.eth.estimate_gas.side_effect = ContractLogicError("revert")
        provider = RootstockProvider.from_testnet()
        with pytest.raises(GasEstimationError):
            provider.estimate_gas({"to": "0x0000000000000000000000000000000000000001"})

    def test_get_balance_rpc_error(self, mock_web3):
        mock_web3.eth.get_balance.side_effect = Exception("connection refused")
        provider = RootstockProvider.from_testnet(max_retries=1)
        with pytest.raises(RPCError):
            provider.get_balance("0x0000000000000000000000000000000000000001")

    def test_connection_error_retry(self, mock_web3):
        mock_web3.eth.get_balance.side_effect = [
            OSError("connection reset"),
            10**18,
        ]
        provider = RootstockProvider.from_testnet(max_retries=2)
        balance = provider.get_balance("0x0000000000000000000000000000000000000001")
        assert balance == 10**18
        assert mock_web3.eth.get_balance.call_count == 2

    def test_connection_error_exhausted(self, mock_web3):
        mock_web3.eth.get_balance.side_effect = OSError("connection reset")
        provider = RootstockProvider.from_testnet(max_retries=1)
        with pytest.raises(ProviderConnectionError):
            provider.get_balance("0x0000000000000000000000000000000000000001")

    def test_nonce_too_low_detection(self, mock_web3):
        from web3.exceptions import Web3RPCError

        mock_web3.eth.send_raw_transaction.side_effect = Web3RPCError("nonce too low")
        provider = RootstockProvider.from_testnet()
        with pytest.raises(NonceTooLowError):
            provider.send_raw_transaction(b"\x00")
