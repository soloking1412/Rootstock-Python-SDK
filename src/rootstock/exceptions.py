"""SDK exceptions."""

from __future__ import annotations


class RootstockError(Exception):
    pass


class ProviderError(RootstockError):
    pass


class ProviderConnectionError(ProviderError):
    pass


class RPCError(ProviderError):
    def __init__(self, message: str, code: int | None = None, data: dict | None = None):
        self.code = code
        self.data = data
        super().__init__(message)


class WalletError(RootstockError):
    pass


class InvalidPrivateKeyError(WalletError):
    pass


class KeystoreDecryptionError(WalletError):
    pass


class InsufficientFundsError(WalletError):
    pass


class TransactionError(RootstockError):
    pass


class TransactionRevertedError(TransactionError):
    def __init__(self, tx_hash: str, receipt: dict):
        self.tx_hash = tx_hash
        self.receipt = receipt
        super().__init__(f"Transaction {tx_hash} reverted")


class GasEstimationError(TransactionError):
    pass


class NonceTooLowError(TransactionError):
    pass


class ContractError(RootstockError):
    pass


class ContractNotFoundError(ContractError):
    pass


class ABIError(ContractError):
    pass


class TokenError(ContractError):
    pass


class AllowanceExceededError(TokenError):
    pass


class RNSError(RootstockError):
    pass


class DomainNotFoundError(RNSError):
    pass


class ResolverNotFoundError(RNSError):
    pass


class InvalidDomainError(RNSError):
    pass


class AddressError(RootstockError):
    pass


class InvalidAddressError(AddressError):
    pass


