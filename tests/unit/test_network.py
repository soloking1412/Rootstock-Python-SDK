import pytest

from rootstock.network import NetworkConfig


class TestNetworkConfig:
    def test_mainnet_defaults(self):
        net = NetworkConfig.mainnet()
        assert net.chain_id == 30
        assert net.rpc_url == "https://public-node.rsk.co"
        assert "blockscout" in net.explorer_url
        assert net.name == "Rootstock Mainnet"

    def test_mainnet_custom_rpc(self):
        net = NetworkConfig.mainnet(rpc_url="https://my-node.example.com")
        assert net.rpc_url == "https://my-node.example.com"
        assert net.chain_id == 30

    def test_testnet_defaults(self):
        net = NetworkConfig.testnet()
        assert net.chain_id == 31
        assert "testnet" in net.rpc_url
        assert net.name == "Rootstock Testnet"

    def test_custom_network(self):
        net = NetworkConfig.custom(
            chain_id=33,
            rpc_url="http://localhost:4444",
            name="RegTest",
        )
        assert net.chain_id == 33
        assert net.rpc_url == "http://localhost:4444"
        assert net.name == "RegTest"
        assert net.explorer_url == ""

    def test_frozen(self):
        net = NetworkConfig.mainnet()
        with pytest.raises(AttributeError):
            net.chain_id = 99  # type: ignore[misc]

    def test_tx_url(self):
        net = NetworkConfig.mainnet()
        url = net.tx_url("0xabc123")
        assert url.endswith("/tx/0xabc123")
        assert url.startswith("https://")

    def test_tx_url_no_explorer(self):
        net = NetworkConfig.custom(chain_id=33, rpc_url="http://localhost:4444")
        assert net.tx_url("0xabc") == ""

    def test_address_url(self):
        net = NetworkConfig.testnet()
        url = net.address_url("0xdef456")
        assert url.endswith("/address/0xdef456")

    def test_address_url_no_explorer(self):
        net = NetworkConfig.custom(chain_id=33, rpc_url="http://localhost:4444")
        assert net.address_url("0xdef") == ""

    def test_equality(self):
        a = NetworkConfig.mainnet()
        b = NetworkConfig.mainnet()
        assert a == b

    def test_inequality(self):
        a = NetworkConfig.mainnet()
        b = NetworkConfig.testnet()
        assert a != b
