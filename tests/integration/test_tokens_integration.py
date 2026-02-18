import pytest

from rootstock.tokens import ERC20Token


@pytest.mark.integration
class TestERC20TokenIntegration:
    def test_rif_token_info(self, mainnet_provider):
        rif = ERC20Token.from_symbol(mainnet_provider, "RIF")
        assert "RIF" in rif.name()
        assert rif.symbol() == "RIF"
        assert rif.decimals() == 18

    def test_rif_total_supply(self, mainnet_provider):
        rif = ERC20Token.from_symbol(mainnet_provider, "RIF")
        supply = rif.total_supply()
        assert supply > 0

    def test_rif_balance_of_zero_address(self, mainnet_provider):
        rif = ERC20Token.from_symbol(mainnet_provider, "RIF")
        balance = rif.balance_of("0x0000000000000000000000000000000000000000")
        assert isinstance(balance, int)

    def test_trif_testnet(self, testnet_provider):
        trif = ERC20Token.from_symbol(testnet_provider, "tRIF")
        decimals = trif.decimals()
        assert decimals == 18
