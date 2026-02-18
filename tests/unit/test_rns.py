from unittest.mock import MagicMock, patch

import pytest

from rootstock.constants import ZERO_ADDRESS, ChainId
from rootstock.exceptions import (
    DomainNotFoundError,
    InvalidDomainError,
    ResolverNotFoundError,
)
from rootstock.rns import RNS

MOCK_REGISTRY_ADDR = "0xcb868aeabd31e2b66f74e9a55cf064abb31a4ad5"
MOCK_RESOLVER_ADDR = "0x4efd25e3d348f8f25a14fb7655fba6f72edfe93a"
MOCK_RESOLVED_ADDR = "0x1234567890abcdef1234567890abcdef12345678"


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.chain_id = ChainId.MAINNET
    provider.w3 = MagicMock()
    return provider


@pytest.fixture
def rns(mock_provider):
    with patch("rootstock.rns._load_abi", return_value=[
        {
            "constant": True,
            "inputs": [{"name": "node", "type": "bytes32"}],
            "name": "resolver",
            "outputs": [{"name": "", "type": "address"}],
            "type": "function",
            "stateMutability": "view",
        },
        {
            "constant": True,
            "inputs": [{"name": "node", "type": "bytes32"}],
            "name": "owner",
            "outputs": [{"name": "", "type": "address"}],
            "type": "function",
            "stateMutability": "view",
        },
    ]):
        return RNS(mock_provider)


class TestRNSResolve:
    def test_resolve_domain(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = MOCK_RESOLVER_ADDR

        resolver_contract = MagicMock()
        resolver_contract.functions.addr.return_value.call.return_value = MOCK_RESOLVED_ADDR

        mock_provider.w3.eth.contract.side_effect = [
            registry_contract,
            resolver_contract,
        ]

        # Re-create RNS since we changed side_effect above
        with patch("rootstock.rns._load_abi", return_value=[
            {
                "constant": True,
                "inputs": [{"name": "node", "type": "bytes32"}],
                "name": "resolver",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function",
                "stateMutability": "view",
            },
            {
                "constant": True,
                "inputs": [{"name": "node", "type": "bytes32"}],
                "name": "owner",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function",
                "stateMutability": "view",
            },
        ]):
            mock_provider.w3.eth.contract.side_effect = None
            mock_provider.w3.eth.contract.return_value = registry_contract
            rns_inst = RNS(mock_provider)

        def contract_factory(address, abi):
            if address.lower() == MOCK_RESOLVER_ADDR.lower():
                return resolver_contract
            return registry_contract

        mock_provider.w3.eth.contract.side_effect = contract_factory
        rns_inst._registry = registry_contract

        result = rns_inst.resolve("alice.rsk")
        assert result.lower() == MOCK_RESOLVED_ADDR.lower()

    def test_resolve_adds_rsk_suffix(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = MOCK_RESOLVER_ADDR

        resolver_contract = MagicMock()
        resolver_contract.functions.addr.return_value.call.return_value = MOCK_RESOLVED_ADDR
        mock_provider.w3.eth.contract.side_effect = lambda address, abi: resolver_contract

        rns._registry = registry_contract
        result = rns.resolve("alice")  # should auto-append .rsk
        assert result.lower() == MOCK_RESOLVED_ADDR.lower()

    def test_resolve_zero_address_raises(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = MOCK_RESOLVER_ADDR

        resolver_contract = MagicMock()
        resolver_contract.functions.addr.return_value.call.return_value = ZERO_ADDRESS
        mock_provider.w3.eth.contract.side_effect = lambda address, abi: resolver_contract

        rns._registry = registry_contract
        with pytest.raises(DomainNotFoundError, match="zero address"):
            rns.resolve("nonexistent.rsk")

    def test_resolve_no_resolver_raises(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = ZERO_ADDRESS

        rns._registry = registry_contract
        with pytest.raises(ResolverNotFoundError, match="No resolver"):
            rns.resolve("noreslover.rsk")


class TestRNSReverseResolve:
    def test_reverse_resolve(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = MOCK_RESOLVER_ADDR

        resolver_contract = MagicMock()
        resolver_contract.functions.name.return_value.call.return_value = "alice.rsk"
        mock_provider.w3.eth.contract.side_effect = lambda address, abi: resolver_contract

        rns._registry = registry_contract
        result = rns.reverse_resolve(MOCK_RESOLVED_ADDR)
        assert result == "alice.rsk"

    def test_reverse_resolve_no_resolver(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = ZERO_ADDRESS

        rns._registry = registry_contract
        result = rns.reverse_resolve(MOCK_RESOLVED_ADDR)
        assert result is None

    def test_reverse_resolve_no_name(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.resolver.return_value.call.return_value = MOCK_RESOLVER_ADDR

        resolver_contract = MagicMock()
        resolver_contract.functions.name.return_value.call.return_value = ""
        mock_provider.w3.eth.contract.side_effect = lambda address, abi: resolver_contract

        rns._registry = registry_contract
        result = rns.reverse_resolve(MOCK_RESOLVED_ADDR)
        assert result is None


class TestRNSOwnership:
    def test_get_owner(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.owner.return_value.call.return_value = MOCK_RESOLVED_ADDR

        rns._registry = registry_contract
        owner = rns.get_owner("alice.rsk")
        assert owner.lower() == MOCK_RESOLVED_ADDR.lower()

    def test_is_available_true(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.owner.return_value.call.return_value = ZERO_ADDRESS

        rns._registry = registry_contract
        assert rns.is_available("unclaimed.rsk") is True

    def test_is_available_false(self, rns, mock_provider):
        registry_contract = mock_provider.w3.eth.contract.return_value
        registry_contract.functions.owner.return_value.call.return_value = MOCK_RESOLVED_ADDR

        rns._registry = registry_contract
        assert rns.is_available("taken.rsk") is False


class TestRNSHelpers:
    def test_ensure_rsk_suffix(self, rns):
        assert rns._ensure_rsk_suffix("alice") == "alice.rsk"
        assert rns._ensure_rsk_suffix("alice.rsk") == "alice.rsk"
        assert rns._ensure_rsk_suffix("ALICE") == "alice.rsk"
        assert rns._ensure_rsk_suffix("  alice  ") == "alice.rsk"

    def test_validate_domain_empty_label(self, rns):
        with pytest.raises(InvalidDomainError):
            rns._validate_domain("alice..rsk")

    def test_validate_domain_valid(self, rns):
        rns._validate_domain("alice.rsk")  # should not raise
