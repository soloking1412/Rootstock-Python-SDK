# Quick Start

## Installation

```bash
pip install rootstock-sdk
```

## Connect to Rootstock

```python
from rootstock import RootstockProvider

# Testnet (for development)
provider = RootstockProvider.from_testnet()

# Mainnet (for production)
provider = RootstockProvider.from_mainnet()

# Custom node
provider = RootstockProvider.from_url("https://my-node.com", chain_id=30)

# Check connection
print(provider.is_connected)
print(provider.get_block_number())
```

## Create a Wallet

```python
from rootstock import Wallet, ChainId

# New random wallet
wallet = Wallet.create(chain_id=ChainId.TESTNET)
print(wallet.address)

# From private key
wallet = Wallet.from_private_key("0x...", chain_id=ChainId.TESTNET)
```

## Send RBTC

```python
from rootstock import RootstockProvider, Wallet, TransactionBuilder, ChainId

provider = RootstockProvider.from_testnet()
wallet = Wallet.from_private_key("0x...", chain_id=ChainId.TESTNET)
tx = TransactionBuilder(provider, wallet)

receipt = tx.transfer(to="0xRECIPIENT", value_rbtc=0.001)
print(f"Status: {receipt['status']}")
```

## Check Token Balance

```python
from rootstock import RootstockProvider, ERC20Token

provider = RootstockProvider.from_mainnet()
rif = ERC20Token.from_symbol(provider, "RIF")
balance = rif.balance_of_human("0xADDRESS")
print(f"Balance: {balance} RIF")
```

## Resolve RNS Domain

```python
from rootstock import RootstockProvider, RNS

provider = RootstockProvider.from_mainnet()
rns = RNS(provider)
address = rns.resolve("alice.rsk")
```
