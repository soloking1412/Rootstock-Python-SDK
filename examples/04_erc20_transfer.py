"""Example: ERC-20 token operations."""

from rootstock import ERC20Token, RootstockProvider

# Connect to mainnet
provider = RootstockProvider.from_mainnet()

# Load RIF token by symbol
rif = ERC20Token.from_symbol(provider, "RIF")
print(f"Token: {rif.name()}")
print(f"Symbol: {rif.symbol()}")
print(f"Decimals: {rif.decimals()}")

# Check balance of an address
address = "0x0000000000000000000000000000000000000001"
balance = rif.balance_of(address)
human_balance = rif.balance_of_human(address)
print(f"\nBalance of {address}: {human_balance} RIF")

# Load WRBTC
wrbtc = ERC20Token.from_symbol(provider, "WRBTC")
print(f"\nWRBTC: {wrbtc.name()}")

# Transfer tokens (uncomment with funded wallet)
# wallet = Wallet.from_private_key("0x...", chain_id=ChainId.MAINNET)
# receipt = rif.transfer(wallet, to="0xRECIPIENT", amount=100 * 10**18)
# print(f"Transfer TX: {receipt['transactionHash'].hex()}")
