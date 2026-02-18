import pytest

from rootstock.constants import ChainId


@pytest.mark.integration
class TestProviderIntegration:
    def test_is_connected(self, testnet_provider):
        assert testnet_provider.is_connected is True

    def test_chain_id(self, testnet_provider):
        assert testnet_provider.chain_id == ChainId.TESTNET

    def test_get_block_number(self, testnet_provider):
        block = testnet_provider.get_block_number()
        assert isinstance(block, int)
        assert block > 0

    def test_get_gas_price(self, testnet_provider):
        gas_price = testnet_provider.get_gas_price()
        assert isinstance(gas_price, int)
        assert gas_price > 0

    def test_get_block(self, testnet_provider):
        block = testnet_provider.get_block("latest")
        assert "number" in block
        assert "hash" in block

    def test_get_balance(self, testnet_provider):
        balance = testnet_provider.get_balance(
            "0x0000000000000000000000000000000000000000"
        )
        assert isinstance(balance, int)
        assert balance >= 0

    def test_get_transaction_count(self, testnet_provider):
        count = testnet_provider.get_transaction_count(
            "0x0000000000000000000000000000000000000000"
        )
        assert isinstance(count, int)
        assert count >= 0

    def test_get_code_eoa(self, testnet_provider):
        code = testnet_provider.get_code(
            "0x0000000000000000000000000000000000000001"
        )
        assert isinstance(code, bytes)


@pytest.mark.integration
class TestMainnetProviderIntegration:
    def test_is_connected(self, mainnet_provider):
        assert mainnet_provider.is_connected is True

    def test_chain_id(self, mainnet_provider):
        assert mainnet_provider.chain_id == ChainId.MAINNET

    def test_get_block_number(self, mainnet_provider):
        block = mainnet_provider.get_block_number()
        assert block > 4_000_000  # Mainnet has millions of blocks
