# Smart Contracts

The `Contract` class provides a generic wrapper for interacting with any smart contract on Rootstock.

## Loading Contracts

```python
from rootstock import RootstockProvider, Contract

provider = RootstockProvider.from_testnet()

# From ABI list
contract = Contract(provider, "0xCONTRACT_ADDRESS", abi=[...])

# From ABI file
contract = Contract.from_abi_file(provider, "0xCONTRACT_ADDRESS", "path/to/abi.json")
```

## Read-Only Calls

```python
# Call a view function
result = contract.call("greet")

# With arguments
result = contract.call("balanceOf", "0xADDRESS")

# At a specific block
result = contract.call("totalSupply", block=1000000)
```

## State-Changing Transactions

```python
from rootstock import Wallet, ChainId

wallet = Wallet.from_private_key("0x...", chain_id=ChainId.TESTNET)

# Simple write
receipt = contract.transact(wallet, "setGreeting", "Hello!")

# With value (payable functions)
receipt = contract.transact(wallet, "deposit", value=10**18)

# Custom gas
receipt = contract.transact(wallet, "setGreeting", "Hi!", gas_limit=100000)

# Don't wait for mining
tx_hash = contract.transact(wallet, "setGreeting", "Hi!", wait=False)
```

## Encoding Calldata

```python
# Useful for multicall or manual transaction building
data = contract.encode_function_data("setGreeting", "Hello!")
```

## Events

```python
# Fetch past events
events = contract.get_events("Transfer", from_block=0, to_block="latest")

# With filters
events = contract.get_events(
    "Transfer",
    from_block=1000000,
    filters={"from": "0xADDRESS"},
)
```

## Introspection

```python
print(contract.functions)  # ["greet", "setGreeting", ...]
print(contract.events)     # ["GreetingChanged", ...]
print(contract.address)    # "0x..."

# Access underlying web3.py contract
w3_contract = contract.web3_contract
```
