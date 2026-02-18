import pytest

from rootstock._utils.checksum import (
    is_checksum_address,
    normalize_address,
    to_checksum_address,
)
from rootstock.exceptions import InvalidAddressError


class TestNormalizeAddress:
    def test_valid_lowercase(self):
        addr = "0x27b1fdb04752bbc536007a920d24acb045561c26"
        assert normalize_address(addr) == addr

    def test_valid_mixed_case(self):
        addr = "0x27B1FdB04752BbC536007A920D24ACB045561C26"
        assert normalize_address(addr) == addr.lower()

    def test_invalid_too_short(self):
        with pytest.raises(InvalidAddressError):
            normalize_address("0x1234")

    def test_invalid_no_prefix(self):
        with pytest.raises(InvalidAddressError):
            normalize_address("27b1fdb04752bbc536007a920d24acb045561c26")

    def test_invalid_non_hex(self):
        with pytest.raises(InvalidAddressError):
            normalize_address("0xZZZZfdb04752bbc536007a920d24acb045561c26")

    def test_invalid_type(self):
        with pytest.raises(InvalidAddressError):
            normalize_address(12345)  # type: ignore[arg-type]


class TestToChecksumAddress:
    def test_eip55_no_chain_id(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        result = to_checksum_address(addr)
        assert result == "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"

    def test_rsk_mainnet_chain_30(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        result = to_checksum_address(addr, chain_id=30)
        assert result.lower() == addr.lower()
        assert result.startswith("0x")
        assert len(result) == 42

    def test_rsk_testnet_chain_31(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        result = to_checksum_address(addr, chain_id=31)
        assert result.lower() == addr.lower()
        assert result.startswith("0x")
        assert len(result) == 42

    def test_different_chain_ids_produce_different_checksums(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        eip55 = to_checksum_address(addr)
        rsk30 = to_checksum_address(addr, chain_id=30)
        rsk31 = to_checksum_address(addr, chain_id=31)
        results = {eip55, rsk30, rsk31}
        assert len(results) >= 2

    def test_zero_address(self):
        addr = "0x0000000000000000000000000000000000000000"
        result = to_checksum_address(addr, chain_id=30)
        assert result.lower() == addr.lower()

    def test_all_ones(self):
        addr = "0xffffffffffffffffffffffffffffffffffffffff"
        result = to_checksum_address(addr, chain_id=30)
        assert result.lower() == addr.lower()

    def test_idempotent(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        first = to_checksum_address(addr, chain_id=30)
        second = to_checksum_address(first, chain_id=30)
        assert first == second

    def test_invalid_address_raises(self):
        with pytest.raises(InvalidAddressError):
            to_checksum_address("0xinvalid")


class TestIsChecksumAddress:
    def test_valid_eip55(self):
        addr = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
        assert is_checksum_address(addr) is True

    def test_invalid_eip55(self):
        addr = "0x5AAEB6053F3E94C9B9A09F33669435E7EF1BEAED"
        assert is_checksum_address(addr) is False

    def test_valid_rsk_chain_id(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        checksummed = to_checksum_address(addr, chain_id=30)
        assert is_checksum_address(checksummed, chain_id=30) is True

    def test_wrong_chain_id(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        checksummed = to_checksum_address(addr, chain_id=30)
        # Validating with a different chain_id should generally fail
        # (unless by coincidence the checksums match)
        result_31 = is_checksum_address(checksummed, chain_id=31)
        result_none = is_checksum_address(checksummed, chain_id=None)
        assert not (result_31 and result_none)

    def test_invalid_format(self):
        assert is_checksum_address("not-an-address") is False

    def test_lowercase_fails_eip55(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        assert is_checksum_address(addr) is False
