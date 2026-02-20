"""Transaction building and broadcasting for Rootstock (legacy format only)."""

from __future__ import annotations

import logging
import threading
from decimal import Decimal

from rootstock._utils.checksum import normalize_address_for_web3
from rootstock._utils.units import from_wei, to_wei
from rootstock.constants import DEFAULT_GAS_LIMIT_TRANSFER
from rootstock.exceptions import InsufficientFundsError
from rootstock.provider import RootstockProvider
from rootstock.wallet import Wallet

logger = logging.getLogger(__name__)


class TransactionBuilder:

    def __init__(self, provider: RootstockProvider, wallet: Wallet):
        self._provider = provider
        self._wallet = wallet
        self._lock = threading.Lock()
        self._nonce_offset = 0
        self._last_base_nonce: int | None = None

    def transfer(
        self,
        to: str,
        value_rbtc: float | str | Decimal | None = None,
        value_wei: int | None = None,
        gas_limit: int | None = None,
        gas_price: int | None = None,
        nonce: int | None = None,
        wait: bool = True,
        timeout: int = 120,
    ) -> dict | str:
        if value_wei is not None:
            value = value_wei
        elif value_rbtc is not None:
            value = to_wei(value_rbtc, "rbtc")
        else:
            value = 0

        tx_dict = self.build_transaction(
            to=to,
            value=value,
            gas_limit=gas_limit or DEFAULT_GAS_LIMIT_TRANSFER,
            gas_price=gas_price,
            nonce=nonce,
        )
        return self.sign_and_send(tx_dict, wait=wait, timeout=timeout)

    def build_transaction(
        self,
        to: str,
        value: int = 0,
        data: bytes | str = b"",
        gas_limit: int | None = None,
        gas_price: int | None = None,
        nonce: int | None = None,
    ) -> dict:
        to_addr = normalize_address_for_web3(to)
        from_addr = normalize_address_for_web3(self._wallet.address)

        if isinstance(data, str) and data.startswith("0x"):
            data_hex = data
        elif isinstance(data, bytes):
            data_hex = "0x" + data.hex() if data else "0x"
        else:
            data_hex = "0x"

        actual_nonce = nonce if nonce is not None else self._auto_nonce()
        actual_gas_price = gas_price if gas_price is not None else self._auto_gas_price()

        tx: dict = {
            "from": from_addr,
            "to": to_addr,
            "value": value,
            "data": data_hex,
            "nonce": actual_nonce,
            "gasPrice": actual_gas_price,
            "chainId": self._provider.chain_id,
        }

        if gas_limit is not None:
            tx["gas"] = gas_limit
        else:
            tx["gas"] = self._provider.estimate_gas(tx)

        logger.debug("Built transaction: to=%s, value=%d, nonce=%d", tx["to"], tx["value"], tx["nonce"])
        return tx

    def sign_and_send(
        self,
        tx_dict: dict,
        wait: bool = True,
        timeout: int = 120,
    ) -> dict | str:
        with self._lock:
            balance = self._provider.get_balance(self._wallet.address)
            total_needed = tx_dict.get("value", 0) + tx_dict["gas"] * tx_dict["gasPrice"]
            if balance < total_needed:
                raise InsufficientFundsError(
                    f"Insufficient funds: balance {balance} wei < required {total_needed} wei"
                )

            signed_tx = self._wallet.sign_transaction(tx_dict)
            tx_hash = self._provider.send_raw_transaction(signed_tx)

        if wait:
            return self._provider.wait_for_transaction(tx_hash, timeout=timeout)
        return tx_hash

    def estimate_total_cost(
        self,
        to: str,
        value: int = 0,
        data: bytes | str = b"",
    ) -> dict:
        to_addr = normalize_address_for_web3(to)
        from_addr = normalize_address_for_web3(self._wallet.address)

        if isinstance(data, str) and data.startswith("0x"):
            data_hex = data
        elif isinstance(data, bytes):
            data_hex = "0x" + data.hex() if data else "0x"
        else:
            data_hex = "0x"

        tx_params = {
            "from": from_addr,
            "to": to_addr,
            "value": value,
            "data": data_hex,
        }

        gas = self._provider.estimate_gas(tx_params)
        gas_price = self._auto_gas_price()
        gas_cost = gas * gas_price
        total_cost = value + gas_cost

        return {
            "gas": gas,
            "gas_price": gas_price,
            "gas_cost": gas_cost,
            "value": value,
            "total_cost": total_cost,
            "total_cost_rbtc": str(from_wei(total_cost, "rbtc")),
        }

    def reset_nonce(self) -> None:
        with self._lock:
            self._nonce_offset = 0
            self._last_base_nonce = None

    def _auto_nonce(self) -> int:
        base = self._provider.get_transaction_count(self._wallet.address)
        if self._last_base_nonce is not None and base == self._last_base_nonce:
            self._nonce_offset += 1
        else:
            self._nonce_offset = 0
            self._last_base_nonce = base
        return base + self._nonce_offset

    def _auto_gas_price(self) -> int:
        return self._provider.get_gas_price()
