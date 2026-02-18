# Rootstock Python SDK

[![PyPI](https://img.shields.io/pypi/v/rootstock-sdk)](https://pypi.org/project/rootstock-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/rootstock-sdk)](https://pypi.org/project/rootstock-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python SDK for interacting with the **Rootstock (RSK)** blockchain. Provides wallet management, RBTC transfers, ERC-20 token operations, smart contract interactions, and RNS domain resolution.

## Installation

```bash
pip install rootstock-sdk
```

## Quick Start

```python
from rootstock import RootstockProvider, Wallet, TransactionBuilder, ChainId

# Connect to Rootstock Testnet
provider = RootstockProvider.from_testnet()
print(f"Connected: {provider.is_connected}")
print(f"Block: {provider.get_block_number()}")

# Create a wallet
wallet = Wallet.create(chain_id=ChainId.TESTNET)
print(f"Address: {wallet.address}")

# Import existing wallet
wallet = Wallet.from_private_key("0xYOUR_KEY", chain_id=ChainId.TESTNET)

# Check balance
balance = provider.get_balance(wallet.address)
print(f"Balance: {balance} wei")

# Send RBTC
tx = TransactionBuilder(provider, wallet)
receipt = tx.transfer(to="0xRECIPIENT", value_rbtc=0.001)
print(f"TX Hash: {receipt['transactionHash'].hex()}")
```

## Features

### Wallet Management

```python
from rootstock import Wallet, ChainId

# Create new wallet
wallet = Wallet.create(chain_id=ChainId.MAINNET)

# Import from private key
wallet = Wallet.from_private_key("0x...", chain_id=ChainId.MAINNET)

# Encrypt to keystore
keystore = wallet.encrypt("my-password")

# Decrypt from keystore
wallet = Wallet.from_keystore(keystore, "my-password")

# Sign messages
signature = wallet.sign_message("Hello Rootstock!")
```

### Provider (Network Connection)

```python
from rootstock import RootstockProvider

# Mainnet
provider = RootstockProvider.from_mainnet()

# Testnet
provider = RootstockProvider.from_testnet()

# Custom RPC
provider = RootstockProvider.from_url("https://my-node.com", chain_id=30)

# Query blockchain
balance = provider.get_balance("0x...")
block = provider.get_block("latest")
gas_price = provider.get_gas_price()
```

### Transactions

```python
from rootstock import RootstockProvider, Wallet, TransactionBuilder

provider = RootstockProvider.from_testnet()
wallet = Wallet.from_private_key("0x...", chain_id=31)
tx = TransactionBuilder(provider, wallet)

# Simple transfer
receipt = tx.transfer(to="0x...", value_rbtc=0.001)

# Transfer with options
receipt = tx.transfer(
    to="0x...",
    value_wei=1000000000000000,
    gas_limit=21000,
    gas_price=60000000,
)

# Estimate costs
cost = tx.estimate_total_cost(to="0x...", value=10**18)
print(f"Total cost: {cost['total_cost_rbtc']} RBTC")
```

### ERC-20 Tokens

```python
from rootstock import RootstockProvider, ERC20Token, Wallet

provider = RootstockProvider.from_mainnet()

# Load by address
rif = ERC20Token(provider, "0x2acc95758f8b5f583470ba265eb685a8f45fc9d5")

# Load by symbol
rif = ERC20Token.from_symbol(provider, "RIF")

# Read token info
print(rif.name())        # "RIF"
print(rif.symbol())      # "RIF"
print(rif.decimals())    # 18

# Check balance
balance = rif.balance_of("0x...")
human = rif.balance_of_human("0x...")  # "150.5"

# Transfer tokens
wallet = Wallet.from_private_key("0x...", chain_id=30)
receipt = rif.transfer(wallet, to="0x...", amount=100 * 10**18)

# Approve spender
receipt = rif.approve(wallet, spender="0x...", amount=100 * 10**18)
```

### Smart Contracts

```python
from rootstock import RootstockProvider, Contract, Wallet

provider = RootstockProvider.from_testnet()

# Load contract with ABI
contract = Contract(provider, "0xCONTRACT", abi=[...])

# Or from ABI file
contract = Contract.from_abi_file(provider, "0xCONTRACT", "abi.json")

# Read-only call
result = contract.call("greet")

# State-changing transaction
wallet = Wallet.from_private_key("0x...", chain_id=31)
receipt = contract.transact(wallet, "setGreeting", "Hello!")

# Encode calldata
data = contract.encode_function_data("setGreeting", "Hello!")
```

### RNS (RIF Name Service)

```python
from rootstock import RootstockProvider, RNS

provider = RootstockProvider.from_mainnet()
rns = RNS(provider)

# Forward resolution
address = rns.resolve("alice.rsk")

# Reverse resolution
name = rns.reverse_resolve("0x...")

# Check availability
available = rns.is_available("myname.rsk")

# Get domain owner
owner = rns.get_owner("alice.rsk")
```

### Utilities

```python
from rootstock import to_wei, from_wei, to_checksum_address, is_checksum_address

# Unit conversion
wei = to_wei(1.5, "rbtc")        # 1500000000000000000
rbtc = from_wei(10**18, "rbtc")  # Decimal('1')
gwei = to_wei(60, "gwei")        # 60000000000

# EIP-1191 address checksum (Rootstock-specific)
addr = to_checksum_address("0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed", chain_id=30)
valid = is_checksum_address(addr, chain_id=30)  # True
```

## Supported Networks

| Network | Chain ID | RPC URL |
|---------|----------|---------|
| Mainnet | 30 | `https://public-node.rsk.co` |
| Testnet | 31 | `https://public-node.testnet.rsk.co` |

## Known Tokens

| Token | Network | Address |
|-------|---------|---------|
| WRBTC | Mainnet | `0x542FDA317318eBf1d3DeAF76E0B632741a7e677d` |
| RIF | Mainnet | `0x2acc95758f8b5f583470ba265eb685a8f45fc9d5` |
| tRIF | Testnet | `0x19f64674D8a5b4e652319F5e239EFd3bc969a1FE` |

## Development

```bash
# Clone the repository
git clone https://github.com/rootstock/rootstock-python-sdk.git
cd rootstock-python-sdk

# Create a virtual environment (Python 3.10+)
python3 -m venv .venv

# Activate the virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows (cmd):
# .venv\Scripts\activate.bat
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit/ -v

# Run integration tests (requires internet -- hits live Rootstock testnet/mainnet)
pytest tests/integration/ -v

# Run all tests with coverage
pytest tests/ -v --cov=rootstock --cov-report=term-missing

# Lint
ruff check src/ tests/

# Build package
python -m build
```

## Requirements

- Python >= 3.10
- web3.py >= 7.0, < 8.0
- eth-account >= 0.13, < 1.0

## License

MIT
