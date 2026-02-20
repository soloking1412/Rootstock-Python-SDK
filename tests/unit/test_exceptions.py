from rootstock.exceptions import (
    ABIError,
    AddressError,
    AllowanceExceededError,
    ContractError,
    ContractNotFoundError,
    DomainNotFoundError,
    GasEstimationError,
    InsufficientFundsError,
    InvalidAddressError,
    InvalidDomainError,
    InvalidPrivateKeyError,
    KeystoreDecryptionError,
    NonceTooLowError,
    ProviderConnectionError,
    ProviderError,
    ResolverNotFoundError,
    RNSError,
    RootstockError,
    RPCError,
    TokenError,
    TransactionError,
    TransactionRevertedError,
    WalletError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_rootstock_error(self):
        exceptions = [
            ProviderError, ProviderConnectionError, RPCError,
            WalletError, InvalidPrivateKeyError, KeystoreDecryptionError,
            InsufficientFundsError,
            TransactionError, TransactionRevertedError, GasEstimationError,
            NonceTooLowError,
            ContractError, ContractNotFoundError, ABIError,
            TokenError, AllowanceExceededError,
            RNSError, DomainNotFoundError, ResolverNotFoundError, InvalidDomainError,
            AddressError, InvalidAddressError,
        ]
        for exc_cls in exceptions:
            assert issubclass(exc_cls, RootstockError), f"{exc_cls.__name__} not subclass"

    def test_provider_hierarchy(self):
        assert issubclass(ProviderConnectionError, ProviderError)
        assert issubclass(RPCError, ProviderError)

    def test_wallet_hierarchy(self):
        assert issubclass(InvalidPrivateKeyError, WalletError)
        assert issubclass(KeystoreDecryptionError, WalletError)
        assert issubclass(InsufficientFundsError, WalletError)

    def test_transaction_hierarchy(self):
        assert issubclass(TransactionRevertedError, TransactionError)
        assert issubclass(GasEstimationError, TransactionError)
        assert issubclass(NonceTooLowError, TransactionError)

    def test_contract_hierarchy(self):
        assert issubclass(ContractNotFoundError, ContractError)
        assert issubclass(ABIError, ContractError)
        assert issubclass(TokenError, ContractError)
        assert issubclass(AllowanceExceededError, TokenError)

    def test_rns_hierarchy(self):
        assert issubclass(DomainNotFoundError, RNSError)
        assert issubclass(ResolverNotFoundError, RNSError)
        assert issubclass(InvalidDomainError, RNSError)

    def test_address_hierarchy(self):
        assert issubclass(InvalidAddressError, AddressError)


class TestRPCError:
    def test_with_code_and_data(self):
        exc = RPCError("bad request", code=-32600, data={"info": "test"})
        assert exc.code == -32600
        assert exc.data == {"info": "test"}
        assert "bad request" in str(exc)

    def test_without_code(self):
        exc = RPCError("generic error")
        assert exc.code is None
        assert exc.data is None


class TestTransactionRevertedError:
    def test_attributes(self):
        receipt = {"status": 0, "gasUsed": 21000}
        exc = TransactionRevertedError("0xabc", receipt)
        assert exc.tx_hash == "0xabc"
        assert exc.receipt == receipt
        assert "0xabc" in str(exc)
