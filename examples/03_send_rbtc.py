"""Example: Send RBTC on testnet."""

from rootstock import ChainId, RootstockProvider, TransactionBuilder, Wallet, from_wei, to_wei

# Connect to testnet
provider = RootstockProvider.from_testnet()

# Import wallet (use a funded testnet wallet)
wallet = Wallet.from_private_key("0xYOUR_PRIVATE_KEY", chain_id=ChainId.TESTNET)
print(f"Sender: {wallet.address}")

# Check balance
balance = provider.get_balance(wallet.address)
print(f"Balance: {from_wei(balance, 'rbtc')} RBTC")

tx = TransactionBuilder(provider, wallet)

# Estimate cost
recipient = "0x0000000000000000000000000000000000000001"
cost = tx.estimate_total_cost(to=recipient, value=to_wei(0.001, "rbtc"))
print(f"Estimated gas: {cost['gas']}")
print(f"Total cost: {cost['total_cost_rbtc']} RBTC")

# Send RBTC (uncomment with funded wallet)
# receipt = tx.transfer(to=recipient, value_rbtc=0.001)
# print(f"TX Hash: {receipt['transactionHash'].hex()}")
# print(f"Status: {'Success' if receipt['status'] == 1 else 'Failed'}")
# print(f"Gas Used: {receipt['gasUsed']}")
