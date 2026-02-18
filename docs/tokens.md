# ERC-20 Tokens

The `ERC20Token` class provides high-level methods for interacting with ERC-20 token contracts on Rootstock.

## Loading Tokens

```python
from rootstock import RootstockProvider, ERC20Token

provider = RootstockProvider.from_mainnet()

# By address
token = ERC20Token(provider, "0x2acc95758f8b5f583470ba265eb685a8f45fc9d5")

# By well-known symbol
rif = ERC20Token.from_symbol(provider, "RIF")
wrbtc = ERC20Token.from_symbol(provider, "WRBTC")

# Testnet tokens
testnet = RootstockProvider.from_testnet()
trif = ERC20Token.from_symbol(testnet, "tRIF")
```

## Reading Token Info

```python
print(rif.name())         # "RIF Token"
print(rif.symbol())       # "RIF"
print(rif.decimals())     # 18
print(rif.total_supply())  # Total supply in smallest unit
```

## Checking Balances

```python
# Raw balance (smallest unit)
balance = rif.balance_of("0xADDRESS")

# Human-readable
human = rif.balance_of_human("0xADDRESS")  # e.g., "150.5"

# Allowance
allowed = rif.allowance(owner="0xOWNER", spender="0xSPENDER")
```

## Transfers

```python
from rootstock import Wallet, ChainId

wallet = Wallet.from_private_key("0x...", chain_id=ChainId.MAINNET)

# Transfer tokens
receipt = rif.transfer(wallet, to="0xRECIPIENT", amount=100 * 10**18)

# Approve a spender
receipt = rif.approve(wallet, spender="0xSPENDER", amount=100 * 10**18)

# Transfer using allowance
receipt = rif.transfer_from(wallet, from_address="0xOWNER", to="0xTO", amount=50 * 10**18)
```

## Known Tokens

| Symbol | Network | Address |
|--------|---------|---------|
| WRBTC | Mainnet (30) | `0x542FDA317318eBf1d3DeAF76E0B632741a7e677d` |
| RIF | Mainnet (30) | `0x2acc95758f8b5f583470ba265eb685a8f45fc9d5` |
| tRIF | Testnet (31) | `0x19f64674D8a5b4e652319F5e239EFd3bc969a1FE` |
