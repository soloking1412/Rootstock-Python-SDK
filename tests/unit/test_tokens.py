from unittest.mock import MagicMock

import pytest

from rootstock.constants import ChainId
from rootstock.exceptions import TokenError
from rootstock.tokens import ERC20Token

RIF_MAINNET = "0x2acc95758f8b5f583470ba265eb685a8f45fc9d5"
TRIF_TESTNET = "0x19f64674D8a5b4e652319F5e239EFd3bc969a1FE"


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.chain_id = ChainId.MAINNET
    provider.w3 = MagicMock()
    mock_contract = MagicMock()
    provider.w3.eth.contract.return_value = mock_contract
    return provider


@pytest.fixture
def mock_testnet_provider():
    provider = MagicMock()
    provider.chain_id = ChainId.TESTNET
    provider.w3 = MagicMock()
    mock_contract = MagicMock()
    provider.w3.eth.contract.return_value = mock_contract
    return provider


class TestERC20Construction:
    def test_create_with_address(self, mock_provider):
        token = ERC20Token(mock_provider, RIF_MAINNET)
        assert token.address.lower() == RIF_MAINNET.lower()

    def test_from_symbol_rif(self, mock_provider):
        token = ERC20Token.from_symbol(mock_provider, "RIF")
        assert token.address.lower() == RIF_MAINNET.lower()

    def test_from_symbol_case_insensitive(self, mock_provider):
        token = ERC20Token.from_symbol(mock_provider, "rif")
        assert token.address.lower() == RIF_MAINNET.lower()

    def test_from_symbol_wrbtc(self, mock_provider):
        token = ERC20Token.from_symbol(mock_provider, "WRBTC")
        assert token.address.lower() == "0x542fda317318ebf1d3deaf76e0b632741a7e677d"

    def test_from_symbol_trif_testnet(self, mock_testnet_provider):
        token = ERC20Token.from_symbol(mock_testnet_provider, "tRIF")
        assert token.address.lower() == TRIF_TESTNET.lower()

    def test_from_symbol_unknown_raises(self, mock_provider):
        with pytest.raises(TokenError, match="Unknown token"):
            ERC20Token.from_symbol(mock_provider, "UNKNOWN")

    def test_from_symbol_wrong_network_raises(self, mock_testnet_provider):
        with pytest.raises(TokenError, match="not available"):
            ERC20Token.from_symbol(mock_testnet_provider, "WRBTC")

    def test_repr(self, mock_provider):
        token = ERC20Token(mock_provider, RIF_MAINNET)
        assert "ERC20Token(" in repr(token)


class TestERC20ReadMethods:
    def test_name(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.name.return_value.call.return_value = (
            "RIF Token"
        )
        token = ERC20Token(mock_provider, RIF_MAINNET)
        assert token.name() == "RIF Token"

    def test_symbol(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.symbol.return_value.call.return_value = (
            "RIF"
        )
        token = ERC20Token(mock_provider, RIF_MAINNET)
        assert token.symbol() == "RIF"

    def test_decimals(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.decimals.return_value.call.return_value = (
            18
        )
        token = ERC20Token(mock_provider, RIF_MAINNET)
        assert token.decimals() == 18

    def test_total_supply(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.totalSupply.return_value.call.return_value = (
            10**27
        )
        token = ERC20Token(mock_provider, RIF_MAINNET)
        assert token.total_supply() == 10**27

    def test_balance_of(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.balanceOf.return_value.call.return_value = (
            500 * 10**18
        )
        token = ERC20Token(mock_provider, RIF_MAINNET)
        balance = token.balance_of("0x0000000000000000000000000000000000000001")
        assert balance == 500 * 10**18

    def test_allowance(self, mock_provider):
        mock_provider.w3.eth.contract.return_value.functions.allowance.return_value.call.return_value = (
            100 * 10**18
        )
        token = ERC20Token(mock_provider, RIF_MAINNET)
        allowance = token.allowance(
            "0x0000000000000000000000000000000000000001",
            "0x0000000000000000000000000000000000000002",
        )
        assert allowance == 100 * 10**18

    def test_balance_of_human(self, mock_provider):
        contract = mock_provider.w3.eth.contract.return_value
        contract.functions.balanceOf.return_value.call.return_value = 1_500_000_000_000_000_000
        contract.functions.decimals.return_value.call.return_value = 18

        token = ERC20Token(mock_provider, RIF_MAINNET)
        result = token.balance_of_human("0x0000000000000000000000000000000000000001")
        assert result == "1.5"
