"""Rootstock provider wrapping web3.py with RSK-specific configuration."""

from __future__ import annotations

import logging
import time

from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted, Web3RPCError
from web3.middleware import ExtraDataToPOAMiddleware

from rootstock._utils.checksum import normalize_address_for_web3
from rootstock.exceptions import (
    GasEstimationError,
    NonceTooLowError,
    ProviderConnectionError,
    RPCError,
    TransactionError,
    TransactionRevertedError,
)
from rootstock.network import NetworkConfig
from rootstock.types import BlockIdentifier

logger = logging.getLogger(__name__)


class RootstockProvider:
    """web3.py connection to a Rootstock node with POA middleware
    and legacy transaction support (no EIP-1559)."""

    def __init__(self, network: NetworkConfig, request_timeout: int = 30, max_retries: int = 3):
        self._network = network
        self._max_retries = max_retries
        self._w3 = self._configure_web3(network.rpc_url, request_timeout)
        logger.info("Connected to %s (chain_id=%d)", network.name, network.chain_id)

    @classmethod
    def from_mainnet(
        cls, rpc_url: str | None = None, request_timeout: int = 30, max_retries: int = 3
    ) -> RootstockProvider:
        return cls(NetworkConfig.mainnet(rpc_url), request_timeout, max_retries)

    @classmethod
    def from_testnet(
        cls, rpc_url: str | None = None, request_timeout: int = 30, max_retries: int = 3
    ) -> RootstockProvider:
        return cls(NetworkConfig.testnet(rpc_url), request_timeout, max_retries)

    @classmethod
    def from_url(
        cls, rpc_url: str, chain_id: int, request_timeout: int = 30, max_retries: int = 3
    ) -> RootstockProvider:
        network = NetworkConfig.custom(chain_id=chain_id, rpc_url=rpc_url)
        return cls(network, request_timeout, max_retries)

    @classmethod
    def from_websocket(
        cls, ws_url: str, chain_id: int, request_timeout: int = 30, max_retries: int = 3
    ) -> RootstockProvider:
        network = NetworkConfig.custom(chain_id=chain_id, rpc_url=ws_url)
        return cls(network, request_timeout, max_retries)

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
        return self._call_with_retry(
            self._w3.eth.get_balance, normalize_address_for_web3(address), block
        )

    def get_transaction_count(
        self, address: str, block: BlockIdentifier = "latest"
    ) -> int:
        return self._call_with_retry(
            self._w3.eth.get_transaction_count, normalize_address_for_web3(address), block
        )

    def get_block(
        self, block: BlockIdentifier = "latest", full_transactions: bool = False
    ) -> dict:
        result = self._call_with_retry(self._w3.eth.get_block, block, full_transactions)
        return dict(result)

    def get_block_number(self) -> int:
        return self._call_with_retry(lambda: self._w3.eth.block_number)

    def get_transaction(self, tx_hash: str) -> dict:
        result = self._call_with_retry(self._w3.eth.get_transaction, tx_hash)
        return dict(result)

    def get_transaction_receipt(self, tx_hash: str) -> dict | None:
        receipt = self._call_with_retry(self._w3.eth.get_transaction_receipt, tx_hash)
        return dict(receipt) if receipt else None

    def get_gas_price(self) -> int:
        return self._call_with_retry(lambda: self._w3.eth.gas_price)

    def estimate_gas(self, tx_params: dict) -> int:
        try:
            return self._w3.eth.estimate_gas(tx_params)
        except ContractLogicError as exc:
            raise GasEstimationError(f"Gas estimation failed: {exc}") from exc
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def get_code(self, address: str, block: BlockIdentifier = "latest") -> bytes:
        result = self._call_with_retry(
            self._w3.eth.get_code, normalize_address_for_web3(address), block
        )
        return bytes(result)

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
            result = tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash)
            logger.info("Transaction sent: %s", result)
            return result
        except Exception as exc:
            logger.error("Failed to send transaction: %s", exc)
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

    def _call_with_retry(self, fn, *args):
        last_exc = None
        for attempt in range(self._max_retries):
            try:
                return fn(*args)
            except (OSError, ConnectionResetError) as exc:
                last_exc = exc
                if attempt < self._max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(
                        "RPC call failed (attempt %d/%d), retrying in %ds: %s",
                        attempt + 1, self._max_retries, delay, exc,
                    )
                    time.sleep(delay)
            except Exception as exc:
                raise self._wrap_error(exc) from exc
        raise self._wrap_error(last_exc) from last_exc

    def _configure_web3(self, rpc_url: str, timeout: int) -> Web3:
        if rpc_url.startswith("ws://") or rpc_url.startswith("wss://"):
            from web3 import WebSocketProvider

            provider = WebSocketProvider(rpc_url)
        else:
            provider = Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": timeout})

        w3 = Web3(provider)
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        return w3

    def _wrap_error(self, error: Exception) -> Exception:
        if isinstance(error, OSError):
            logger.error("Connection error: %s", error)
            return ProviderConnectionError(f"Cannot connect to RPC: {error}")
        if isinstance(error, Web3RPCError):
            msg = str(error).lower()
            if "nonce too low" in msg or "nonce is too low" in msg:
                return NonceTooLowError(str(error))
            logger.error("RPC error: %s", error)
            return RPCError(str(error))
        if isinstance(error, (TransactionError, GasEstimationError)):
            return error
        logger.error("Unexpected error: %s", error)
        return RPCError(f"RPC error: {error}")
