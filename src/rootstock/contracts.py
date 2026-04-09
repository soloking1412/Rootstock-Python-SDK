"""Smart contract interaction wrapper for Rootstock."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from web3.contract import Contract as Web3Contract
from web3.exceptions import ContractLogicError

from rootstock._utils.checksum import normalize_address_for_web3
from rootstock.exceptions import ABIError, ContractError, ContractNotFoundError, RPCError
from rootstock.provider import RootstockProvider
from rootstock.transactions import TransactionBuilder
from rootstock.wallet import Wallet

logger = logging.getLogger(__name__)


class Contract:
    def __init__(
        self, provider: RootstockProvider, address: str, abi: list[dict], *, verify: bool = True
    ):
        if not abi:
            raise ABIError("ABI cannot be empty")

        self._provider = provider
        self._address = normalize_address_for_web3(address)

        if verify:
            code = provider.get_code(self._address)
            if not code:
                raise ContractNotFoundError(f"No contract code at address {address}")

        self._abi = abi
        self._contract: Web3Contract = provider.w3.eth.contract(address=self._address, abi=abi)

    @classmethod
    def from_abi_file(
        cls, provider: RootstockProvider, address: str, abi_path: str | Path
    ) -> Contract:
        """Load contract from a JSON ABI file on disk."""
        path = Path(abi_path)
        if not path.exists():
            raise ABIError(f"ABI file not found: {path}")
        try:
            abi = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ABIError(f"Failed to load ABI from {path}: {exc}") from exc
        return cls(provider, address, abi)

    def call(self, function_name: str, *args, block: str | int = "latest", **kwargs) -> object:
        """Call a read-only contract function."""
        fn = self._get_function(function_name)
        try:
            return fn(*args, **kwargs).call(block_identifier=block)
        except ContractLogicError as exc:
            raise ContractError(f"Call to {function_name} reverted: {exc}") from exc
        except Exception as exc:
            raise RPCError(f"Call to {function_name} failed: {exc}") from exc

    def transact(
        self,
        wallet: Wallet,
        function_name: str,
        *args,
        value: int = 0,
        gas_limit: int | None = None,
        gas_price: int | None = None,
        nonce: int | None = None,
        wait: bool = True,
        timeout: int = 120,
        tx_builder: TransactionBuilder | None = None,
        **kwargs,
    ) -> dict | str:
        """Send a state-changing transaction to a contract function."""
        fn = self._get_function(function_name)
        builder = tx_builder or TransactionBuilder(self._provider, wallet)

        data = fn(*args, **kwargs).build_transaction(
            {"from": normalize_address_for_web3(wallet.address), "gas": 0}
        )["data"]

        tx_dict = builder.build_transaction(
            to=self._address,
            value=value,
            data=data,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
        )
        return builder.sign_and_send(tx_dict, wait=wait, timeout=timeout)

    def encode_function_data(self, function_name: str, *args, **kwargs) -> str:
        """Return ABI-encoded call data for a function."""
        fn = self._get_function(function_name)
        data = fn(*args, **kwargs).build_transaction({"from": "0x" + "0" * 40, "gas": 0})["data"]
        return data

    def get_events(
        self,
        event_name: str,
        from_block: int = 0,
        to_block: int | str = "latest",
        filters: dict | None = None,
    ) -> list[dict]:
        """Fetch historical events via eth_getLogs."""
        try:
            event = self._contract.events[event_name]
        except (KeyError, AttributeError) as exc:
            raise ABIError(f"Event {event_name!r} not found in ABI") from exc

        try:
            kwargs: dict = {"fromBlock": from_block, "toBlock": to_block}
            if filters:
                kwargs["argument_filters"] = filters
            entries = event.get_logs(**kwargs)
            return [dict(e) for e in entries]
        except Exception as exc:
            raise RPCError(f"Failed to fetch events: {exc}") from exc

    @property
    def functions(self) -> list[str]:
        return [item["name"] for item in self._abi if item.get("type") == "function"]

    @property
    def events(self) -> list[str]:
        return [item["name"] for item in self._abi if item.get("type") == "event"]

    @property
    def address(self) -> str:
        return self._address

    @property
    def web3_contract(self) -> Web3Contract:
        return self._contract

    def _get_function(self, name: str):
        try:
            return self._contract.functions[name]
        except (KeyError, AttributeError) as exc:
            raise ABIError(f"Function {name!r} not found in ABI") from exc

    def __repr__(self) -> str:
        return f"Contract(address={self._address!r}, functions={len(self.functions)})"
