"""Example: Connect to Rootstock and query basic info."""

from rootstock import RootstockProvider

# Connect to testnet
provider = RootstockProvider.from_testnet()

print(f"Connected: {provider.is_connected}")
print(f"Chain ID: {provider.chain_id}")
print(f"Network: {provider.network.name}")
print(f"Block Number: {provider.get_block_number()}")
print(f"Gas Price: {provider.get_gas_price()} wei")

# Connect to mainnet
mainnet = RootstockProvider.from_mainnet()
print(f"\nMainnet Block: {mainnet.get_block_number()}")
