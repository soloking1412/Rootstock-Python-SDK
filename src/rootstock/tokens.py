"""ERC-20 token interaction for Rootstock."""

from __future__ import annotations

import json
from decimal import Decimal
from importlib.resources import files as pkg_files

from web3 import Web3

from rootstock.constants import TOKENS, ChainId
from rootstock.exceptions import RPCError, TokenError
from rootstock.provider import RootstockProvider
from rootstock.transactions import TransactionBuilder
from rootstock.wallet import Wallet


def _load_erc20_abi() -> list[dict]:
    abi_dir = pkg_files("rootstock._abi")
    return json.loads((abi_dir / "erc20.json").read_text(encoding="utf-8"))


class ERC20Token:

    def __init__(
        self,
        provider: RootstockProvider,
        token_address: str,
        abi: list | None = None,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(token_address.lower())
        self._abi = abi or _load_erc20_abi()
        self._contract = provider.w3.eth.contract(address=self._address, abi=self._abi)

    @classmethod
    def from_symbol(cls, provider: RootstockProvider, symbol: str) -> ERC20Token:
        symbol_upper = symbol.upper()
        for token_name, addresses in TOKENS.items():
            if token_name.upper() == symbol_upper:
                chain_id = ChainId(provider.chain_id)
                if chain_id in addresses:
                    return cls(provider, addresses[chain_id])
                raise TokenError(
                    f"Token {symbol!r} not available on chain ID {provider.chain_id}"
                )
        raise TokenError(f"Unknown token symbol: {symbol!r}")

    def name(self) -> str:
        try:
            return self._contract.functions.name().call()
        except Exception as exc:
            raise RPCError(f"Failed to get token name: {exc}") from exc

    def symbol(self) -> str:
        try:
            return self._contract.functions.symbol().call()
        except Exception as exc:
            raise RPCError(f"Failed to get token symbol: {exc}") from exc

    def decimals(self) -> int:
        try:
            return self._contract.functions.decimals().call()
        except Exception as exc:
            raise RPCError(f"Failed to get token decimals: {exc}") from exc

    def total_supply(self) -> int:
        try:
            return self._contract.functions.totalSupply().call()
        except Exception as exc:
            raise RPCError(f"Failed to get total supply: {exc}") from exc

    def balance_of(self, address: str) -> int:
        try:
            addr = Web3.to_checksum_address(address.lower())
            return self._contract.functions.balanceOf(addr).call()
        except Exception as exc:
            raise RPCError(f"Failed to get balance: {exc}") from exc

    def allowance(self, owner: str, spender: str) -> int:
        try:
            owner_addr = Web3.to_checksum_address(owner.lower())
            spender_addr = Web3.to_checksum_address(spender.lower())
            return self._contract.functions.allowance(owner_addr, spender_addr).call()
        except Exception as exc:
            raise RPCError(f"Failed to get allowance: {exc}") from exc

    def balance_of_human(self, address: str) -> str:
        raw = self.balance_of(address)
        dec = self.decimals()
        value = Decimal(str(raw)) / Decimal(10**dec)
        return str(value)

    def transfer(
        self,
        wallet: Wallet,
        to: str,
        amount: int,
        gas_limit: int | None = None,
        gas_price: int | None = None,
        wait: bool = True,
        timeout: int = 120,
    ) -> dict | str:
        to_addr = Web3.to_checksum_address(to.lower())
        from_addr = Web3.to_checksum_address(wallet.address.lower())

        data = self._contract.functions.transfer(to_addr, amount).build_transaction(
            {"from": from_addr, "gas": 0}
        )["data"]

        tx_builder = TransactionBuilder(self._provider, wallet)
        tx_dict = tx_builder.build_transaction(
            to=self._address,
            data=data,
            gas_limit=gas_limit,
            gas_price=gas_price,
        )
        return tx_builder.sign_and_send(tx_dict, wait=wait, timeout=timeout)

    def approve(
        self,
        wallet: Wallet,
        spender: str,
        amount: int,
        gas_limit: int | None = None,
        gas_price: int | None = None,
        wait: bool = True,
        timeout: int = 120,
    ) -> dict | str:
        spender_addr = Web3.to_checksum_address(spender.lower())
        from_addr = Web3.to_checksum_address(wallet.address.lower())

        data = self._contract.functions.approve(spender_addr, amount).build_transaction(
            {"from": from_addr, "gas": 0}
        )["data"]

        tx_builder = TransactionBuilder(self._provider, wallet)
        tx_dict = tx_builder.build_transaction(
            to=self._address,
            data=data,
            gas_limit=gas_limit,
            gas_price=gas_price,
        )
        return tx_builder.sign_and_send(tx_dict, wait=wait, timeout=timeout)

    def transfer_from(
        self,
        wallet: Wallet,
        from_address: str,
        to: str,
        amount: int,
        gas_limit: int | None = None,
        gas_price: int | None = None,
        wait: bool = True,
        timeout: int = 120,
    ) -> dict | str:
        from_addr = Web3.to_checksum_address(from_address.lower())
        to_addr = Web3.to_checksum_address(to.lower())
        sender_addr = Web3.to_checksum_address(wallet.address.lower())

        data = self._contract.functions.transferFrom(
            from_addr, to_addr, amount
        ).build_transaction({"from": sender_addr, "gas": 0})["data"]

        tx_builder = TransactionBuilder(self._provider, wallet)
        tx_dict = tx_builder.build_transaction(
            to=self._address,
            data=data,
            gas_limit=gas_limit,
            gas_price=gas_price,
        )
        return tx_builder.sign_and_send(tx_dict, wait=wait, timeout=timeout)

    @property
    def address(self) -> str:
        return self._address

    def __repr__(self) -> str:
        return f"ERC20Token(address={self._address!r})"
