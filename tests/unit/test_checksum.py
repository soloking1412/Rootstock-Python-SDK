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

    # EIP-1191 / RSKIP-60 reference vectors
    def test_eip1191_chain30_vector1(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        assert (
            to_checksum_address(addr, chain_id=30) == "0x5aaEB6053f3e94c9b9a09f33669435E7ef1bEAeD"
        )

    def test_eip1191_chain31_vector1(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        assert (
            to_checksum_address(addr, chain_id=31) == "0x5aAeb6053F3e94c9b9A09F33669435E7EF1BEaEd"
        )

    def test_eip1191_chain30_vector2(self):
        addr = "0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359"
        assert (
            to_checksum_address(addr, chain_id=30) == "0xFb6916095cA1Df60bb79ce92cE3EA74c37c5d359"
        )

    def test_eip1191_chain31_vector2(self):
        addr = "0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359"
        assert (
            to_checksum_address(addr, chain_id=31) == "0xFb6916095CA1dF60bb79CE92ce3Ea74C37c5D359"
        )

    def test_eip1191_chain30_vector3(self):
        addr = "0xdbf03b407c01e7cd3cbea99509d93f8dddc8c6fb"
        assert (
            to_checksum_address(addr, chain_id=30) == "0xDBF03B407c01E7CD3cBea99509D93F8Dddc8C6FB"
        )

    def test_eip1191_chain31_vector3(self):
        addr = "0xdbf03b407c01e7cd3cbea99509d93f8dddc8c6fb"
        assert (
            to_checksum_address(addr, chain_id=31) == "0xdbF03B407C01E7cd3cbEa99509D93f8dDDc8C6fB"
        )

    def test_eip1191_chain30_vector4(self):
        addr = "0xd9b4beebb9dd27ff78c5c65b2feed2f4ca4db3d4"
        assert (
            to_checksum_address(addr, chain_id=30) == "0xd9b4BEeBb9dd27ff78c5c65b2fEED2f4cA4db3d4"
        )

    def test_eip1191_chain31_vector4(self):
        addr = "0xd9b4beebb9dd27ff78c5c65b2feed2f4ca4db3d4"
        assert (
            to_checksum_address(addr, chain_id=31) == "0xd9b4BEEBb9dd27fF78C5C65B2fEEd2f4Ca4Db3d4"
        )


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
        result_31 = is_checksum_address(checksummed, chain_id=31)
        result_none = is_checksum_address(checksummed, chain_id=None)
        assert not (result_31 and result_none)

    def test_invalid_format(self):
        assert is_checksum_address("not-an-address") is False

    def test_lowercase_fails_eip55(self):
        addr = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
        assert is_checksum_address(addr) is False
