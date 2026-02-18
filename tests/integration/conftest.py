import os

import pytest

from rootstock.provider import RootstockProvider


@pytest.fixture(scope="session")
def testnet_provider():
    rpc_url = os.environ.get(
        "ROOTSTOCK_TESTNET_RPC", "https://public-node.testnet.rsk.co"
    )
    try:
        provider = RootstockProvider.from_testnet(rpc_url=rpc_url)
        if not provider.is_connected:
            pytest.skip("Cannot connect to Rootstock Testnet")
        return provider
    except Exception:
        pytest.skip("Cannot connect to Rootstock Testnet")


@pytest.fixture(scope="session")
def mainnet_provider():
    rpc_url = os.environ.get("ROOTSTOCK_MAINNET_RPC", "https://public-node.rsk.co")
    try:
        provider = RootstockProvider.from_mainnet(rpc_url=rpc_url)
        if not provider.is_connected:
            pytest.skip("Cannot connect to Rootstock Mainnet")
        return provider
    except Exception:
        pytest.skip("Cannot connect to Rootstock Mainnet")
