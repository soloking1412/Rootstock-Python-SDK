import json
import tempfile
from unittest.mock import MagicMock

import pytest

from rootstock.contracts import Contract
from rootstock.exceptions import ABIError, ContractNotFoundError, RPCError
from rootstock.transactions import TransactionBuilder
from rootstock.wallet import Wallet

SAMPLE_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "greet",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
        "stateMutability": "view",
    },
    {
        "constant": False,
        "inputs": [{"name": "greeting", "type": "string"}],
        "name": "setGreeting",
        "outputs": [],
        "type": "function",
        "stateMutability": "nonpayable",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "setter", "type": "address"},
            {"indexed": False, "name": "greeting", "type": "string"},
        ],
        "name": "GreetingChanged",
        "type": "event",
    },
]

CONTRACT_ADDR = "0x0000000000000000000000000000000000000042"
TEST_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.chain_id = 31
    provider.w3 = MagicMock()
    provider.get_code.return_value = b"\x60\x80"

    mock_contract = MagicMock()
    provider.w3.eth.contract.return_value = mock_contract
    return provider


@pytest.fixture
def wallet():
    return Wallet.from_private_key(TEST_KEY, chain_id=31)


class TestContractConstruction:
    def test_create_with_abi(self, mock_provider):
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        assert contract.address.lower() == CONTRACT_ADDR.lower()

    def test_empty_abi_raises(self, mock_provider):
        with pytest.raises(ABIError, match="cannot be empty"):
            Contract(mock_provider, CONTRACT_ADDR, [])

    def test_from_abi_file(self, mock_provider):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(SAMPLE_ABI, f)
            f.flush()
            contract = Contract.from_abi_file(mock_provider, CONTRACT_ADDR, f.name)
            assert contract.address.lower() == CONTRACT_ADDR.lower()

    def test_from_abi_file_not_found(self, mock_provider):
        with pytest.raises(ABIError, match="not found"):
            Contract.from_abi_file(mock_provider, CONTRACT_ADDR, "/nonexistent/abi.json")


class TestContractProperties:
    def test_functions_list(self, mock_provider):
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        assert "greet" in contract.functions
        assert "setGreeting" in contract.functions

    def test_events_list(self, mock_provider):
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        assert "GreetingChanged" in contract.events

    def test_web3_contract_property(self, mock_provider):
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        assert contract.web3_contract is not None

    def test_repr(self, mock_provider):
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        r = repr(contract)
        assert "Contract(" in r
        assert "functions=" in r


class TestContractCall:
    def test_call_read_function(self, mock_provider):
        mock_fn = MagicMock()
        mock_fn.return_value.call.return_value = "Hello!"
        mock_provider.w3.eth.contract.return_value.functions.__getitem__ = MagicMock(
            return_value=mock_fn
        )

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        result = contract.call("greet")
        assert result == "Hello!"

    def test_call_unknown_function_raises(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.__getitem__ = MagicMock(
            side_effect=KeyError("unknown")
        )
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        with pytest.raises(ABIError, match="not found"):
            contract.call("nonexistent")


class TestContractNotFound:
    def test_no_code_at_address_raises(self, mock_provider):
        mock_provider.get_code.return_value = b""
        with pytest.raises(ContractNotFoundError, match="No contract code"):
            Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)

    def test_none_code_at_address_raises(self, mock_provider):
        mock_provider.get_code.return_value = b""
        with pytest.raises(ContractNotFoundError):
            Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)

    def test_valid_code_passes(self, mock_provider):
        mock_provider.get_code.return_value = b"\x60\x80\x60\x40"
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        assert contract.address.lower() == CONTRACT_ADDR.lower()

    def test_verify_false_skips_code_check(self, mock_provider):
        mock_provider.get_code.return_value = b""
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI, verify=False)
        assert contract.address.lower() == CONTRACT_ADDR.lower()
        mock_provider.get_code.assert_not_called()


class TestContractTransact:
    def test_transact_sends_transaction(self, mock_provider, wallet):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_fn = MagicMock()
        mock_fn.return_value.build_transaction.return_value = {"data": "0xabcd"}
        mock_contract.functions.__getitem__ = MagicMock(return_value=mock_fn)

        mock_provider.get_transaction_count.return_value = 0
        mock_provider.get_gas_price.return_value = 60_000_000
        mock_provider.estimate_gas.return_value = 21_000
        mock_provider.send_raw_transaction.return_value = "0x" + "ab" * 32
        mock_provider.wait_for_transaction.return_value = {"status": 1}

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        result = contract.transact(wallet, "setGreeting", "Hello")
        assert result["status"] == 1
        mock_provider.send_raw_transaction.assert_called_once()

    def test_transact_uses_provided_tx_builder(self, mock_provider, wallet):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_fn = MagicMock()
        mock_fn.return_value.build_transaction.return_value = {"data": "0xabcd"}
        mock_contract.functions.__getitem__ = MagicMock(return_value=mock_fn)

        mock_provider.get_transaction_count.return_value = 0
        mock_provider.get_gas_price.return_value = 60_000_000
        mock_provider.estimate_gas.return_value = 21_000
        mock_provider.send_raw_transaction.return_value = "0x" + "ab" * 32
        mock_provider.wait_for_transaction.return_value = {"status": 1}

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        external_builder = TransactionBuilder(mock_provider, wallet)
        result = contract.transact(wallet, "setGreeting", "Hello", tx_builder=external_builder)
        assert result["status"] == 1

    def test_transact_unknown_function_raises(self, mock_provider, wallet):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_contract.functions.__getitem__ = MagicMock(side_effect=KeyError("x"))

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        with pytest.raises(ABIError, match="not found"):
            contract.transact(wallet, "nonexistent")


class TestContractEncodeFunctionData:
    def test_encode_returns_hex_string(self, mock_provider):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_fn = MagicMock()
        mock_fn.return_value.build_transaction.return_value = {"data": "0xdeadbeef"}
        mock_contract.functions.__getitem__ = MagicMock(return_value=mock_fn)

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        data = contract.encode_function_data("setGreeting", "Hello")
        assert data == "0xdeadbeef"

    def test_encode_unknown_function_raises(self, mock_provider):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_contract.functions.__getitem__ = MagicMock(side_effect=KeyError("x"))

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        with pytest.raises(ABIError, match="not found"):
            contract.encode_function_data("nonexistent")


class TestContractGetEvents:
    def test_get_events_returns_list(self, mock_provider):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_event = MagicMock()
        mock_event.get_logs.return_value = [{"args": {"greeting": "Hi"}, "blockNumber": 1}]
        mock_contract.events.__getitem__ = MagicMock(return_value=mock_event)

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        events = contract.get_events("GreetingChanged", from_block=0, to_block=100)
        assert len(events) == 1
        mock_event.get_logs.assert_called_once_with(fromBlock=0, toBlock=100)

    def test_get_events_with_filters(self, mock_provider):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_event = MagicMock()
        mock_event.get_logs.return_value = []
        mock_contract.events.__getitem__ = MagicMock(return_value=mock_event)

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        contract.get_events("GreetingChanged", filters={"setter": CONTRACT_ADDR})
        mock_event.get_logs.assert_called_once_with(
            fromBlock=0, toBlock="latest", argument_filters={"setter": CONTRACT_ADDR}
        )

    def test_get_events_unknown_event_raises(self, mock_provider):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_contract.events.__getitem__ = MagicMock(side_effect=KeyError("x"))

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        with pytest.raises(ABIError, match="not found"):
            contract.get_events("NonExistentEvent")

    def test_get_events_rpc_error_raises(self, mock_provider):
        mock_contract = mock_provider.w3.eth.contract.return_value
        mock_event = MagicMock()
        mock_event.get_logs.side_effect = Exception("connection error")
        mock_contract.events.__getitem__ = MagicMock(return_value=mock_event)

        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        with pytest.raises(RPCError, match="Failed to fetch events"):
            contract.get_events("GreetingChanged")
