"""Example: Generic smart contract interaction."""

from rootstock import RootstockProvider

# Connect to testnet
provider = RootstockProvider.from_testnet()

# Example ABI for a simple Greeter contract
GREETER_ABI = [
    {
        "inputs": [],
        "name": "greet",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "_greeting", "type": "string"}],
        "name": "setGreeting",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# Load contract (replace with your deployed contract address)
# contract = Contract(provider, "0xYOUR_CONTRACT", abi=GREETER_ABI)

# Read-only call
# greeting = contract.call("greet")
# print(f"Current greeting: {greeting}")

# Write call (requires funded wallet)
# wallet = Wallet.from_private_key("0x...", chain_id=ChainId.TESTNET)
# receipt = contract.transact(wallet, "setGreeting", "Hello from Python!")
# print(f"TX: {receipt['transactionHash'].hex()}")

# Load from ABI file
# contract = Contract.from_abi_file(provider, "0xADDRESS", "path/to/abi.json")

print("Contract interaction example (uncomment with deployed contract)")
