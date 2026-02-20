import json

import pytest

from rootstock.constants import ChainId
from rootstock.exceptions import InvalidPrivateKeyError, KeystoreDecryptionError
from rootstock.wallet import Wallet, WalletInfo

# Hardhat account #0
TEST_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
TEST_ADDR_LOWER = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"


class TestWalletCreation:
    def test_create_mainnet(self):
        wallet = Wallet.create(chain_id=ChainId.MAINNET)
        assert wallet.address.startswith("0x")
        assert len(wallet.address) == 42
        assert wallet.chain_id == 30

    def test_create_testnet(self):
        wallet = Wallet.create(chain_id=ChainId.TESTNET)
        assert wallet.chain_id == 31

    def test_create_default_mainnet(self):
        wallet = Wallet.create()
        assert wallet.chain_id == ChainId.MAINNET

    def test_create_unique_keys(self):
        w1 = Wallet.create()
        w2 = Wallet.create()
        assert w1.private_key != w2.private_key
        assert w1.address.lower() != w2.address.lower()


class TestWalletFromPrivateKey:
    def test_hex_string(self):
        wallet = Wallet.from_private_key(TEST_KEY, chain_id=ChainId.TESTNET)
        assert wallet.address.lower() == TEST_ADDR_LOWER

    def test_hex_string_no_prefix(self):
        wallet = Wallet.from_private_key(TEST_KEY[2:], chain_id=ChainId.TESTNET)
        assert wallet.address.lower() == TEST_ADDR_LOWER

    def test_bytes(self):
        key_bytes = bytes.fromhex(TEST_KEY[2:])
        wallet = Wallet.from_private_key(key_bytes, chain_id=ChainId.TESTNET)
        assert wallet.address.lower() == TEST_ADDR_LOWER

    def test_invalid_key_raises(self):
        with pytest.raises(InvalidPrivateKeyError):
            Wallet.from_private_key("0xinvalid")

    def test_empty_key_raises(self):
        with pytest.raises(InvalidPrivateKeyError):
            Wallet.from_private_key("")


class TestWalletKeystore:
    def test_encrypt_decrypt_round_trip(self):
        wallet = Wallet.from_private_key(TEST_KEY, chain_id=ChainId.TESTNET)
        keystore = wallet.encrypt("testpassword")
        assert "crypto" in keystore
        assert "version" in keystore

        restored = Wallet.from_keystore(keystore, "testpassword", chain_id=ChainId.TESTNET)
        assert restored.address.lower() == wallet.address.lower()
        assert restored.private_key == wallet.private_key

    def test_encrypt_decrypt_json_string(self):
        wallet = Wallet.from_private_key(TEST_KEY, chain_id=ChainId.TESTNET)
        keystore = wallet.encrypt("mypass")
        keystore_json = json.dumps(keystore)

        restored = Wallet.from_keystore(keystore_json, "mypass", chain_id=ChainId.TESTNET)
        assert restored.address.lower() == wallet.address.lower()

    def test_wrong_password_raises(self):
        wallet = Wallet.from_private_key(TEST_KEY)
        keystore = wallet.encrypt("correct")
        with pytest.raises(KeystoreDecryptionError):
            Wallet.from_keystore(keystore, "wrong")

    def test_invalid_keystore_raises(self):
        with pytest.raises(KeystoreDecryptionError):
            Wallet.from_keystore({"invalid": True}, "pass")


class TestWalletProperties:
    def test_private_key_property(self):
        wallet = Wallet.from_private_key(TEST_KEY)
        assert wallet.private_key.startswith("0x")
        assert len(wallet.private_key) == 66

    def test_address_is_checksummed(self):
        wallet = Wallet.from_private_key(TEST_KEY, chain_id=ChainId.MAINNET)
        addr = wallet.address
        assert addr.lower() == TEST_ADDR_LOWER

    def test_info_has_no_private_key(self):
        wallet = Wallet.from_private_key(TEST_KEY)
        info = wallet.info
        assert isinstance(info, WalletInfo)
        assert info.address == wallet.address
        assert not hasattr(info, "private_key")

    def test_repr_no_private_key(self):
        wallet = Wallet.from_private_key(TEST_KEY)
        repr_str = repr(wallet)
        assert "Wallet(" in repr_str
        assert TEST_KEY not in repr_str
        assert TEST_KEY[2:] not in repr_str


class TestWalletSigning:
    def test_sign_transaction(self):
        wallet = Wallet.from_private_key(TEST_KEY, chain_id=ChainId.TESTNET)
        tx = {
            "to": "0x0000000000000000000000000000000000000001",
            "value": 0,
            "gas": 21000,
            "gasPrice": 60000000,
            "nonce": 0,
            "chainId": 31,
        }
        signed = wallet.sign_transaction(tx)
        assert isinstance(signed, bytes)
        assert len(signed) > 0

    def test_sign_message(self):
        wallet = Wallet.from_private_key(TEST_KEY, chain_id=ChainId.TESTNET)
        sig = wallet.sign_message("Hello Rootstock!")
        assert isinstance(sig, str)
        assert sig.startswith("0x")
        assert len(sig) > 2

    def test_sign_message_bytes(self):
        wallet = Wallet.from_private_key(TEST_KEY)
        sig = wallet.sign_message(b"Hello bytes!")
        assert isinstance(sig, str)
        assert sig.startswith("0x")
