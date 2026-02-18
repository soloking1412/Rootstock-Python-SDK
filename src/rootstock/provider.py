"""Rootstock provider wrapping web3.py with RSK-specific configuration."""

from __future__ import annotations

from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted, Web3RPCError
from web3.middleware import ExtraDataToPOAMiddleware

from rootstock._utils.checksum import to_checksum_address as rsk_checksum
from rootstock.exceptions import (
    ConnectionError,
    GasEstimationError,
    RPCError,
    TransactionError,
    TransactionRevertedError,
)
from rootstock.network import NetworkConfig
from rootstock.types import BlockIdentifier


def _normalize_input(address: str) -> str:
    """Convert any hex address to EIP-55 for web3.py consumption."""
    return Web3.to_checksum_address(address.lower())


class RootstockProvider:
    """web3.py connection to a Rootstock node with POA middleware
    and legacy transaction support (no EIP-1559)."""

    def __init__(self, network: NetworkConfig, request_timeout: int = 30):
        self._network = network
        self._w3 = self._configure_web3(network.rpc_url, request_timeout)

    @classmethod
    def from_mainnet(
        cls, rpc_url: str | None = None, request_timeout: int = 30
    ) -> RootstockProvider:
        """Create a provider connected to Rootstock Mainnet."""
        return cls(NetworkConfig.mainnet(rpc_url), request_timeout)

    @classmethod
    def from_testnet(
        cls, rpc_url: str | None = None, request_timeout: int = 30
    ) -> RootstockProvider:
        """Create a provider connected to Rootstock Testnet."""
        return cls(NetworkConfig.testnet(rpc_url), request_timeout)

    @classmethod
    def from_url(
        cls, rpc_url: str, chain_id: int, request_timeout: int = 30
    ) -> RootstockProvider:
        """Create a provider from a custom RPC URL and chain ID."""
        network = NetworkConfig.custom(chain_id=chain_id, rpc_url=rpc_url)
        return cls(network, request_timeout)

    @property
    def w3(self) -> Web3:
        return self._w3

    @property
    def network(self) -> NetworkConfig:
        return self._network

    @property
    def chain_id(self) -> int:
        return self._network.chain_id

    @property
    def is_connected(self) -> bool:
        try:
            return self._w3.is_connected()
        except Exception:
            return False

    def get_balance(self, address: str, block: BlockIdentifier = "latest") -> int:
        try:
            return self._w3.eth.get_balance(_normalize_input(address), block)
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_transaction_count(
        self, address: str, block: BlockIdentifier = "latest"
    ) -> int:
        try:
            return self._w3.eth.get_transaction_count(_normalize_input(address), block)
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_block(
        self, block: BlockIdentifier = "latest", full_transactions: bool = False
    ) -> dict:
        try:
            return dict(self._w3.eth.get_block(block, full_transactions))
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_block_number(self) -> int:
        try:
            return self._w3.eth.block_number
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_transaction(self, tx_hash: str) -> dict:
        try:
            return dict(self._w3.eth.get_transaction(tx_hash))
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_transaction_receipt(self, tx_hash: str) -> dict | None:
        try:
            receipt = self._w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt) if receipt else None
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_gas_price(self) -> int:
        try:
            return self._w3.eth.gas_price
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def estimate_gas(self, tx_params: dict) -> int:
        try:
            return self._w3.eth.estimate_gas(tx_params)
        except ContractLogicError as exc:
            raise GasEstimationError(f"Gas estimation failed: {exc}") from exc
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_code(self, address: str, block: BlockIdentifier = "latest") -> bytes:
        try:
            return bytes(self._w3.eth.get_code(_normalize_input(address), block))
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def call(self, tx_params: dict, block: BlockIdentifier = "latest") -> bytes:
        try:
            return bytes(self._w3.eth.call(tx_params, block))
        except ContractLogicError as exc:
            raise RPCError(f"Call reverted: {exc}") from exc
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def send_raw_transaction(self, signed_tx: bytes | str) -> str:
        try:
            tx_hash = self._w3.eth.send_raw_transaction(signed_tx)
            return tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash)
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def wait_for_transaction(
        self, tx_hash: str, timeout: int = 120, poll_interval: float = 2.0
    ) -> dict:
        try:
            receipt = self._w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=timeout, poll_latency=poll_interval
            )
        except TimeExhausted as exc:
            raise TransactionError(
                f"Transaction {tx_hash} not mined within {timeout}s"
            ) from exc
        except Exception as exc:
            raise self._wrap_error(exc) from exc

        receipt_dict = dict(receipt)
        if receipt_dict.get("status") == 0:
            raise TransactionRevertedError(tx_hash, receipt_dict)
        return receipt_dict

    def _configure_web3(self, rpc_url: str, timeout: int) -> Web3:
        provider = Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": timeout})
        w3 = Web3(provider)

        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        return w3

    def _wrap_error(self, error: Exception) -> Exception:
        if isinstance(error, (ConnectionError, OSError)):
            return ConnectionError(f"Cannot connect to RPC: {error}")
        if isinstance(error, Web3RPCError):
            return RPCError(str(error))
        if isinstance(error, (TransactionError, GasEstimationError)):
            return error
        return RPCError(f"RPC error: {error}")

    def _to_rsk_address(self, address: str) -> str:
        return rsk_checksum(address, self._network.chain_id)
