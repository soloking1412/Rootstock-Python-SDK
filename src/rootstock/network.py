"""Network configuration."""

from __future__ import annotations

from dataclasses import dataclass

from rootstock.constants import EXPLORER_URLS, RPC_URLS, ChainId


@dataclass(frozen=True)
class NetworkConfig:

    chain_id: int
    rpc_url: str
    explorer_url: str
    name: str

    @classmethod
    def mainnet(cls, rpc_url: str | None = None) -> NetworkConfig:
        return cls(
            chain_id=ChainId.MAINNET,
            rpc_url=rpc_url or RPC_URLS[ChainId.MAINNET],
            explorer_url=EXPLORER_URLS[ChainId.MAINNET],
            name="Rootstock Mainnet",
        )

    @classmethod
    def testnet(cls, rpc_url: str | None = None) -> NetworkConfig:
        return cls(
            chain_id=ChainId.TESTNET,
            rpc_url=rpc_url or RPC_URLS[ChainId.TESTNET],
            explorer_url=EXPLORER_URLS[ChainId.TESTNET],
            name="Rootstock Testnet",
        )

    @classmethod
    def custom(
        cls,
        chain_id: int,
        rpc_url: str,
        name: str = "Custom",
        explorer_url: str = "",
    ) -> NetworkConfig:
        return cls(
            chain_id=chain_id,
            rpc_url=rpc_url,
            explorer_url=explorer_url,
            name=name,
        )

    def tx_url(self, tx_hash: str) -> str:
        if not self.explorer_url:
            return ""
        return f"{self.explorer_url}/tx/{tx_hash}"

    def address_url(self, address: str) -> str:
        if not self.explorer_url:
            return ""
        return f"{self.explorer_url}/address/{address}"
