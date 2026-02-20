import json
import tempfile
from unittest.mock import MagicMock

import pytest

from rootstock.contracts import Contract
from rootstock.exceptions import ABIError, ContractNotFoundError

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


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.chain_id = 31
    provider.w3 = MagicMock()
    provider.get_code.return_value = b"\x60\x80"

    mock_contract = MagicMock()
    provider.w3.eth.contract.return_value = mock_contract
    return provider


class TestContractConstruction:
    def test_create_with_abi(self, mock_provider):
        contract = Contract(mock_provider, CONTRACT_ADDR, SAMPLE_ABI)
        assert contract.address.lower() == CONTRACT_ADDR.lower()

    def test_empty_abi_raises(self, mock_provider):
        with pytest.raises(ABIError, match="cannot be empty"):
            Contract(mock_provider, CONTRACT_ADDR, [])

    def test_from_abi_file(self, mock_provider):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
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
