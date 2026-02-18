# RNS (RIF Name Service)

The `RNS` class resolves `.rsk` domain names to addresses and vice versa using the Rootstock Name Service.

## Setup

```python
from rootstock import RootstockProvider, RNS

# RNS is available on both mainnet and testnet
provider = RootstockProvider.from_mainnet()
rns = RNS(provider)

# Custom registry (for private deployments)
rns = RNS(provider, registry_address="0xCUSTOM_REGISTRY")
```

## Forward Resolution

Resolve a domain name to an address.

```python
# Full domain
address = rns.resolve("alice.rsk")

# Auto-appends .rsk if missing
address = rns.resolve("alice")  # same as "alice.rsk"

# Subdomains
address = rns.resolve("sub.alice.rsk")
```

## Reverse Resolution

Resolve an address to a domain name.

```python
name = rns.reverse_resolve("0x1234...")
# Returns "alice.rsk" or None if no reverse record
```

## Domain Queries

```python
# Check availability
available = rns.is_available("myname.rsk")  # True if unregistered

# Get owner
owner = rns.get_owner("alice.rsk")  # Returns zero address if not registered

# Get resolver
resolver = rns.get_resolver("alice.rsk")
```

## Contract Addresses

| Contract | Mainnet | Testnet |
|----------|---------|---------|
| Registry | `0xcb868aeabd31e2b66f74e9a55cf064abb31a4ad5` | `0x7d284aaac6e925aad802a53c0c69efe3764597b8` |
| Resolver | `0x4efd25e3d348f8f25a14fb7655fba6f72edfe93a` | -- |

## How It Works

1. **Normalize** the domain name (lowercase, strip trailing dot)
2. **Namehash** the domain using the EIP-137 algorithm
3. **Query the Registry** for the resolver address: `registry.resolver(node)`
4. **Query the Resolver** for the target address: `resolver.addr(node)`
5. **Return** the EIP-1191 checksummed address

For reverse resolution, the reverse node is constructed as `<lowercase_address>.addr.reverse`.
