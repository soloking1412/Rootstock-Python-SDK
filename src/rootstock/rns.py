"""RNS (RIF Name Service) resolution for .rsk domains."""

from __future__ import annotations

import json
from importlib.resources import files as pkg_files

from web3 import Web3

from rootstock._utils.checksum import to_checksum_address as rsk_checksum
from rootstock._utils.namehash import namehash
from rootstock.constants import ADDR_REVERSE_SUFFIX, RNS_REGISTRY, ZERO_ADDRESS, ChainId
from rootstock.exceptions import (
    DomainNotFoundError,
    InvalidDomainError,
    ResolverNotFoundError,
    RPCError,
)
from rootstock.provider import RootstockProvider


def _load_abi(name: str) -> list[dict]:
    abi_dir = pkg_files("rootstock._abi")
    return json.loads((abi_dir / f"{name}.json").read_text(encoding="utf-8"))


class RNS:

    def __init__(
        self,
        provider: RootstockProvider,
        registry_address: str | None = None,
    ):
        self._provider = provider
        chain_id = provider.chain_id

        if registry_address:
            reg_addr = registry_address
        elif chain_id in (ChainId.MAINNET, ChainId.TESTNET):
            reg_addr = RNS_REGISTRY[ChainId(chain_id)]
        else:
            raise ValueError(
                f"No default RNS registry for chain ID {chain_id}. "
                "Provide registry_address explicitly."
            )

        self._registry_address = Web3.to_checksum_address(reg_addr.lower())
        registry_abi = _load_abi("rns_registry")
        self._registry = provider.w3.eth.contract(
            address=self._registry_address, abi=registry_abi
        )
        self._resolver_abi = _load_abi("rns_resolver")

    def resolve(self, domain: str) -> str:
        domain = self._ensure_rsk_suffix(domain)
        self._validate_domain(domain)

        node = namehash(domain)
        resolver_addr = self._get_resolver_address(node, domain)
        resolver = self._get_resolver_contract(resolver_addr)

        try:
            addr = resolver.functions.addr(node).call()
        except Exception as exc:
            raise RPCError(f"Failed to resolve {domain}: {exc}") from exc

        addr_str = str(addr)
        if addr_str == ZERO_ADDRESS:
            raise DomainNotFoundError(f"Domain {domain!r} resolves to zero address")

        return rsk_checksum(addr_str, self._provider.chain_id)

    def reverse_resolve(self, address: str) -> str | None:
        bare = address.lower().replace("0x", "")
        reverse_name = bare + ADDR_REVERSE_SUFFIX
        node = namehash(reverse_name)

        try:
            resolver_addr = self._registry.functions.resolver(node).call()
        except Exception:
            return None

        if str(resolver_addr) == ZERO_ADDRESS:
            return None

        resolver = self._get_resolver_contract(str(resolver_addr))
        try:
            name = resolver.functions.name(node).call()
        except Exception:
            return None

        if not name:
            return None
        return str(name)

    def get_resolver(self, domain: str) -> str:
        domain = self._ensure_rsk_suffix(domain)
        node = namehash(domain)
        return self._get_resolver_address(node, domain)

    def get_owner(self, domain: str) -> str:
        domain = self._ensure_rsk_suffix(domain)
        node = namehash(domain)
        try:
            owner = self._registry.functions.owner(node).call()
            return rsk_checksum(str(owner), self._provider.chain_id)
        except Exception as exc:
            raise RPCError(f"Failed to get owner of {domain}: {exc}") from exc

    def is_available(self, domain: str) -> bool:
        owner = self.get_owner(domain)
        return owner.lower() == ZERO_ADDRESS

    def _ensure_rsk_suffix(self, domain: str) -> str:
        domain = domain.strip().lower()
        if not domain.endswith(".rsk"):
            domain = domain + ".rsk"
        return domain

    def _validate_domain(self, domain: str) -> None:
        if not domain or ".." in domain:
            raise InvalidDomainError(f"Invalid domain: {domain!r}")
        labels = domain.split(".")
        for label in labels:
            if not label:
                raise InvalidDomainError(f"Domain contains empty label: {domain!r}")

    def _get_resolver_address(self, node: bytes, domain: str) -> str:
        try:
            resolver_addr = self._registry.functions.resolver(node).call()
        except Exception as exc:
            raise RPCError(f"Failed to query resolver for {domain}: {exc}") from exc

        if str(resolver_addr) == ZERO_ADDRESS:
            raise ResolverNotFoundError(f"No resolver set for {domain!r}")
        return str(resolver_addr)

    def _get_resolver_contract(self, resolver_address: str):
        addr = Web3.to_checksum_address(resolver_address.lower())
        return self._provider.w3.eth.contract(address=addr, abi=self._resolver_abi)
