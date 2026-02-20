"""Example: RNS domain resolution."""

from rootstock import RNS, RootstockProvider

# Connect to mainnet (RNS is primarily on mainnet)
provider = RootstockProvider.from_mainnet()
rns = RNS(provider)

# Forward resolution: domain -> address
# address = rns.resolve("alice.rsk")
# print(f"alice.rsk -> {address}")

# Reverse resolution: address -> domain
# name = rns.reverse_resolve("0x...")
# print(f"Reverse: {name}")

# Check domain availability
# available = rns.is_available("myname.rsk")
# print(f"myname.rsk available: {available}")

# Get domain owner
# owner = rns.get_owner("alice.rsk")
# print(f"Owner: {owner}")

print("RNS resolution example — uncomment with real domains to test")
