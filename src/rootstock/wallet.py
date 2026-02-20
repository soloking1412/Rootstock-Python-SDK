"""Wallet management."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from eth_account import Account
from eth_account.signers.local import LocalAccount

from rootstock._utils.checksum import to_checksum_address as rsk_checksum
from rootstock.constants import ChainId
from rootstock.exceptions import InvalidPrivateKeyError, KeystoreDecryptionError
from rootstock.types import KeystoreDict, PrivateKey

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WalletInfo:
    """Read-only snapshot of wallet address (safe to log/display)."""

    address: str
    chain_id: int


class Wallet:

    def __init__(self, account: LocalAccount, chain_id: int = ChainId.MAINNET):
        self._account = account
        self._chain_id = chain_id

    @classmethod
    def create(cls, chain_id: int = ChainId.MAINNET) -> Wallet:
        """Generate a new random wallet."""
        account = Account.create()
        logger.info("Created new wallet")
        return cls(account, chain_id)

    @classmethod
    def from_private_key(
        cls, private_key: PrivateKey, chain_id: int = ChainId.MAINNET
    ) -> Wallet:
        try:
            if isinstance(private_key, bytes):
                account = Account.from_key(private_key)
            else:
                key_str = str(private_key)
                if not key_str.startswith("0x"):
                    key_str = "0x" + key_str
                account = Account.from_key(key_str)
        except Exception as exc:
            raise InvalidPrivateKeyError(f"Invalid private key: {exc}") from exc
        return cls(account, chain_id)

    @classmethod
    def from_keystore(
        cls,
        keystore: dict | str,
        password: str,
        chain_id: int = ChainId.MAINNET,
    ) -> Wallet:
        try:
            if isinstance(keystore, str):
                keystore = json.loads(keystore)
            key = Account.decrypt(keystore, password)
            account = Account.from_key(key)
        except Exception as exc:
            raise KeystoreDecryptionError(f"Failed to decrypt keystore: {exc}") from exc
        return cls(account, chain_id)

    @property
    def address(self) -> str:
        return rsk_checksum(self._account.address, self._chain_id)

    @property
    def private_key(self) -> str:
        key = self._account.key
        if isinstance(key, bytes):
            return "0x" + key.hex()
        return str(key)

    @property
    def chain_id(self) -> int:
        return self._chain_id

    @property
    def info(self) -> WalletInfo:
        return WalletInfo(address=self.address, chain_id=self._chain_id)

    def sign_transaction(self, tx_dict: dict) -> bytes:
        signed = self._account.sign_transaction(tx_dict)
        return bytes(signed.raw_transaction)

    def sign_message(self, message: str | bytes) -> str:
        from eth_account.messages import encode_defunct

        if isinstance(message, str):
            msg = encode_defunct(text=message)
        else:
            msg = encode_defunct(primitive=message)
        signed = self._account.sign_message(msg)
        return "0x" + signed.signature.hex()

    def encrypt(self, password: str, kdf: str = "scrypt") -> KeystoreDict:
        return Account.encrypt(self._account.key, password, kdf=kdf)

    def __repr__(self) -> str:
        return f"Wallet(address={self.address!r}, chain_id={self._chain_id})"
