"""EIP-137 namehash for RNS domain resolution."""

from __future__ import annotations

from eth_hash.auto import keccak

from rootstock.exceptions import InvalidDomainError

EMPTY_NODE = b"\x00" * 32


def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        raise InvalidDomainError(f"Domain name must be a string, got {type(name).__name__}")

    name = name.strip().lower()
    if name.endswith("."):
        name = name[:-1]

    if not name:
        return ""

    labels = name.split(".")
    for label in labels:
        if not label:
            raise InvalidDomainError(f"Domain contains empty label: {name!r}")

    return ".".join(labels)


def label_hash(label: str) -> bytes:
    return keccak(label.encode("utf-8"))


def namehash(name: str) -> bytes:
    name = normalize_name(name)
    if not name:
        return EMPTY_NODE

    node = EMPTY_NODE
    labels = name.split(".")
    for label in reversed(labels):
        node = keccak(node + label_hash(label))

    return node
