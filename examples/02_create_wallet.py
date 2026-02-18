"""Example: Create and manage wallets."""

from rootstock import Wallet, ChainId

# Create a new wallet
wallet = Wallet.create(chain_id=ChainId.TESTNET)
print(f"Address: {wallet.address}")
print(f"Private Key: {wallet.private_key}")
print(f"Chain ID: {wallet.chain_id}")

# Encrypt to keystore
keystore = wallet.encrypt("my-secure-password")
print(f"\nKeystore created (version {keystore['version']})")

# Decrypt from keystore
restored = Wallet.from_keystore(keystore, "my-secure-password", chain_id=ChainId.TESTNET)
print(f"Restored address: {restored.address}")
assert restored.address == wallet.address

# Import from private key
imported = Wallet.from_private_key(wallet.private_key, chain_id=ChainId.TESTNET)
print(f"Imported address: {imported.address}")

# Sign a message
signature = wallet.sign_message("Hello Rootstock!")
print(f"\nSignature: 0x{signature[:20]}...")

# Safe wallet info (no private key)
info = wallet.info
print(f"\nWallet info: {info}")
