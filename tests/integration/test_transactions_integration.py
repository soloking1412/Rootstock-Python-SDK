import pytest

from rootstock.constants import ChainId
from rootstock.transactions import TransactionBuilder
from rootstock.wallet import Wallet


@pytest.mark.integration
class TestTransactionBuilderIntegration:
    def test_build_transaction(self, testnet_provider):
        wallet = Wallet.create(chain_id=ChainId.TESTNET)
        tx = TransactionBuilder(testnet_provider, wallet)

        tx_dict = tx.build_transaction(
            to="0x0000000000000000000000000000000000000001",
            value=0,
            gas_limit=21000,
        )
        assert tx_dict["chainId"] == ChainId.TESTNET
        assert tx_dict["gas"] == 21000
        assert tx_dict["nonce"] == 0
        assert tx_dict["gasPrice"] > 0
        assert "maxFeePerGas" not in tx_dict

    def test_estimate_total_cost(self, testnet_provider):
        wallet = Wallet.create(chain_id=ChainId.TESTNET)
        tx = TransactionBuilder(testnet_provider, wallet)

        cost = tx.estimate_total_cost(
            to="0x0000000000000000000000000000000000000001",
            value=0,
        )
        assert cost["gas"] > 0
        assert cost["gas_price"] > 0
        assert cost["total_cost"] > 0
