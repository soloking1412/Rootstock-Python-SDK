# Wallet

The `Wallet` class manages private keys and signing operations. It supports creating new wallets, importing from private keys, and encrypting/decrypting V3 keystores.

## Creating Wallets

```python
from rootstock import Wallet, ChainId

# Generate a new random wallet
wallet = Wallet.create(chain_id=ChainId.MAINNET)

# Default is mainnet
wallet = Wallet.create()  # chain_id=30
```

## Importing Wallets

```python
# From hex string
wallet = Wallet.from_private_key("0xac09...", chain_id=ChainId.TESTNET)

# From hex without prefix
wallet = Wallet.from_private_key("ac09...", chain_id=ChainId.TESTNET)

# From bytes
wallet = Wallet.from_private_key(b"\xac\x09...", chain_id=ChainId.TESTNET)
```

## Keystore Encryption/Decryption

```python
# Encrypt to keystore
keystore = wallet.encrypt("my-password")
# keystore is a dict that can be JSON-serialized

# Decrypt from keystore dict
wallet = Wallet.from_keystore(keystore, "my-password")

# Decrypt from JSON string
import json
wallet = Wallet.from_keystore(json.dumps(keystore), "my-password")
```

## Properties

- `wallet.address` -- EIP-1191 checksummed address for the configured chain
- `wallet.private_key` -- `0x`-prefixed hex string
- `wallet.chain_id` -- The chain ID used for checksumming
- `wallet.info` -- Safe `WalletInfo` snapshot (no private key, safe to log)

## Signing

```python
# Sign a transaction
signed_bytes = wallet.sign_transaction(tx_dict)

# Sign a message (EIP-191)
signature = wallet.sign_message("Hello Rootstock!")
signature = wallet.sign_message(b"Hello bytes!")
```

## Security Notes

- `repr(wallet)` never exposes the private key
- Use `wallet.info` when you need to log wallet details
- Private keys exist only in memory; there is no persistent storage
