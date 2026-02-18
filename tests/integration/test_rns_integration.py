import pytest

from rootstock.constants import ZERO_ADDRESS
from rootstock.rns import RNS


@pytest.mark.integration
class TestRNSIntegration:
    def test_rns_construction(self, mainnet_provider):
        rns = RNS(mainnet_provider)
        assert rns._registry_address is not None

    def test_get_owner_nonexistent(self, mainnet_provider):
        rns = RNS(mainnet_provider)
        owner = rns.get_owner("zzzzzzzzzzzznotarealdomain.rsk")
        assert owner.lower() == ZERO_ADDRESS

    def test_is_available_nonexistent(self, mainnet_provider):
        rns = RNS(mainnet_provider)
        available = rns.is_available("zzzzzzzzzzzznotarealdomain.rsk")
        assert available is True
