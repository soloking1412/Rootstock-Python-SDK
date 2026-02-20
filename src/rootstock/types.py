"""Type aliases and TypedDicts."""

from __future__ import annotations

from typing import TypedDict

PrivateKey = str | bytes
BlockIdentifier = int | str


class KeystoreDict(TypedDict):
    address: str
    crypto: dict
    id: str
    version: int
