import pytest

from rootstock.constants import ChainId
from rootstock.wallet import Wallet


@pytest.mark.integration
class TestWalletIntegration:
    def test_create_wallet_and_check_balance(self, testnet_provider):
        wallet = Wallet.create(chain_id=ChainId.TESTNET)
        balance = testnet_provider.get_balance(wallet.address)
        assert balance == 0

    def test_sign_transaction_valid(self, testnet_provider):
        wallet = Wallet.create(chain_id=ChainId.TESTNET)
        tx = {
            "to": "0x0000000000000000000000000000000000000001",
            "value": 0,
            "gas": 21000,
            "gasPrice": testnet_provider.get_gas_price(),
            "nonce": 0,
            "chainId": ChainId.TESTNET,
        }
        signed = wallet.sign_transaction(tx)
        assert isinstance(signed, bytes)
        assert len(signed) > 0
