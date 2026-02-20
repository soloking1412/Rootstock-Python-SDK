"""Rootstock chain constants."""

from __future__ import annotations

from enum import IntEnum


class ChainId(IntEnum):
    MAINNET = 30
    TESTNET = 31


RPC_URLS: dict[ChainId, str] = {
    ChainId.MAINNET: "https://public-node.rsk.co",
    ChainId.TESTNET: "https://public-node.testnet.rsk.co",
}

EXPLORER_URLS: dict[ChainId, str] = {
    ChainId.MAINNET: "https://rootstock.blockscout.com",
    ChainId.TESTNET: "https://rootstock-testnet.blockscout.com",
}

DERIVATION_PATHS: dict[ChainId, str] = {
    ChainId.MAINNET: "m/44'/137'/0'/0",
    ChainId.TESTNET: "m/44'/37310'/0'/0",
}

RNS_REGISTRY: dict[ChainId, str] = {
    ChainId.MAINNET: "0xcb868aeabd31e2b66f74e9a55cf064abb31a4ad5",
    ChainId.TESTNET: "0x7d284aaac6e925aad802a53c0c69efe3764597b8",
}

TOKENS: dict[str, dict[ChainId, str]] = {
    "WRBTC": {
        ChainId.MAINNET: "0x542FDA317318eBf1d3DeAF76E0B632741a7e677d",
    },
    "RIF": {
        ChainId.MAINNET: "0x2acc95758f8b5f583470ba265eb685a8f45fc9d5",
    },
    "tRIF": {
        ChainId.TESTNET: "0x19f64674D8a5b4e652319F5e239EFd3bc969a1FE",
    },
}

DEFAULT_GAS_LIMIT_TRANSFER = 21_000

ADDR_REVERSE_SUFFIX = ".addr.reverse"

ZERO_ADDRESS = "0x" + "0" * 40
