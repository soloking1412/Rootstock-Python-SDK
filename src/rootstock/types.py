"""Type aliases and TypedDicts."""

from __future__ import annotations

from typing import NotRequired, TypedDict

Address = str
TxHash = str
PrivateKey = str | bytes
Wei = int
BlockIdentifier = int | str


class TxParams(TypedDict):
    """Parameters for building a transaction."""

    to: str
    value: NotRequired[Wei]
    data: NotRequired[str | bytes]
    gas: NotRequired[int]
    gasPrice: NotRequired[Wei]
    nonce: NotRequired[int]
    chainId: NotRequired[int]


class TxReceipt(TypedDict):
    """Simplified transaction receipt."""

    transactionHash: str
    blockNumber: int
    blockHash: str
    from_address: str
    to: str | None
    gasUsed: int
    status: int
    contractAddress: str | None
    logs: list[dict]


class KeystoreDict(TypedDict):
    """V3 keystore JSON structure."""

    address: str
    crypto: dict
    id: str
    version: int
