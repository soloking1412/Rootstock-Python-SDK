"""EIP-1191 chain-specific address checksum (RSKIP-60)."""

from __future__ import annotations

import re

from eth_hash.auto import keccak

from rootstock.exceptions import InvalidAddressError

_ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def normalize_address(address: str) -> str:
    if not isinstance(address, str) or not _ADDR_RE.match(address):
        raise InvalidAddressError(f"Invalid address: {address!r}")
    return address.lower()


def to_checksum_address(address: str, chain_id: int | None = None) -> str:
    normalized = normalize_address(address)
    bare = normalized[2:]  # strip 0x

    prefix = f"{chain_id}0x" if chain_id is not None else ""
    hash_input = (prefix + bare).encode("utf-8")
    addr_hash = keccak(hash_input).hex()

    result = []
    for i, char in enumerate(bare):
        if char in "0123456789":
            result.append(char)
        else:
            result.append(char.upper() if int(addr_hash[i], 16) >= 8 else char)

    return "0x" + "".join(result)


def is_checksum_address(address: str, chain_id: int | None = None) -> bool:
    try:
        return address == to_checksum_address(address, chain_id)
    except InvalidAddressError:
        return False
