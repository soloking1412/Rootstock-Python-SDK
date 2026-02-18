# Transactions

The `TransactionBuilder` class handles building, signing, and broadcasting transactions on Rootstock. All transactions use the legacy format (no EIP-1559).

## Basic Transfer

```python
from rootstock import RootstockProvider, Wallet, TransactionBuilder, ChainId

provider = RootstockProvider.from_testnet()
wallet = Wallet.from_private_key("0x...", chain_id=ChainId.TESTNET)
tx = TransactionBuilder(provider, wallet)

# Send 0.001 RBTC
receipt = tx.transfer(to="0xRECIPIENT", value_rbtc=0.001)
```

## Transfer Options

```python
# Value in Wei
receipt = tx.transfer(to="0x...", value_wei=1000000000000000)

# Custom gas
receipt = tx.transfer(to="0x...", value_rbtc=0.001, gas_limit=21000, gas_price=60000000)

# Don't wait for mining
tx_hash = tx.transfer(to="0x...", value_rbtc=0.001, wait=False)
```

## Building Transactions Manually

```python
# Build without signing
tx_dict = tx.build_transaction(
    to="0x...",
    value=10**18,
    data=b"",
    gas_limit=21000,
)

# Sign and send
receipt = tx.sign_and_send(tx_dict, wait=True)
```

## Cost Estimation

```python
cost = tx.estimate_total_cost(to="0x...", value=10**18)
print(cost)
# {
#     'gas': 21000,
#     'gas_price': 60000000,
#     'gas_cost': 1260000000000,
#     'value': 1000000000000000000,
#     'total_cost': 1000001260000000000,
#     'total_cost_rbtc': '1.00000126',
# }
```

## Auto-fill Behavior

When not provided, the builder auto-fills:
- **nonce**: Fetched from the chain via `get_transaction_count`
- **gasPrice**: Fetched from the node via `get_gas_price`
- **gas**: Estimated via `estimate_gas` (if `gas_limit` not specified)
