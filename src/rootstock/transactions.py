"""Transaction building and broadcasting for Rootstock (legacy format only)."""

from __future__ import annotations

from decimal import Decimal

from web3 import Web3

from rootstock._utils.units import from_wei, to_wei
from rootstock.constants import DEFAULT_GAS_LIMIT_TRANSFER
from rootstock.provider import RootstockProvider
from rootstock.wallet import Wallet


class TransactionBuilder:

    def __init__(self, provider: RootstockProvider, wallet: Wallet):
        self._provider = provider
        self._wallet = wallet

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
        to_addr = Web3.to_checksum_address(to.lower())
        from_addr = Web3.to_checksum_address(self._wallet.address.lower())

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

        return tx

    def sign_and_send(
        self,
        tx_dict: dict,
        wait: bool = True,
        timeout: int = 120,
    ) -> dict | str:
        signed_tx = self._wallet.sign_transaction(tx_dict)
        tx_hash = self._provider.send_raw_transaction(signed_tx)

        if wait:
            return self._provider.wait_for_transaction(tx_hash, timeout=timeout)
        return tx_hash

    def estimate_total_cost(
        self,
        to: str,
        value: int = 0,
        data: bytes = b"",
    ) -> dict:
        to_addr = Web3.to_checksum_address(to.lower())
        from_addr = Web3.to_checksum_address(self._wallet.address.lower())

        tx_params = {
            "from": from_addr,
            "to": to_addr,
            "value": value,
            "data": "0x" + data.hex() if data else "0x",
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

    def _auto_nonce(self) -> int:
        return self._provider.get_transaction_count(self._wallet.address)

    def _auto_gas_price(self) -> int:
        return self._provider.get_gas_price()
