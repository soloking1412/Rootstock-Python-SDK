from decimal import Decimal

import pytest

from rootstock._utils.units import from_wei, to_wei


class TestToWei:
    def test_one_rbtc(self):
        assert to_wei(1, "rbtc") == 10**18

    def test_one_ether(self):
        assert to_wei(1, "ether") == 10**18

    def test_one_gwei(self):
        assert to_wei(1, "gwei") == 10**9

    def test_one_wei(self):
        assert to_wei(1, "wei") == 1

    def test_zero(self):
        assert to_wei(0, "rbtc") == 0

    def test_fractional_rbtc(self):
        assert to_wei(0.001, "rbtc") == 10**15

    def test_string_value(self):
        assert to_wei("1.5", "rbtc") == 1_500_000_000_000_000_000

    def test_decimal_value(self):
        assert to_wei(Decimal("0.1"), "rbtc") == 10**17

    def test_default_unit_is_rbtc(self):
        assert to_wei(1) == 10**18

    def test_unknown_unit_raises(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            to_wei(1, "unknown")

    def test_fractional_wei_raises(self):
        with pytest.raises(ValueError, match="fractional Wei"):
            to_wei(0.1, "wei")

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError, match="Invalid value"):
            to_wei("not-a-number", "rbtc")

    def test_large_value(self):
        assert to_wei(1_000_000, "rbtc") == 10**24

    def test_case_insensitive_unit(self):
        assert to_wei(1, "RBTC") == to_wei(1, "rbtc")


class TestFromWei:
    def test_one_rbtc(self):
        assert from_wei(10**18, "rbtc") == Decimal("1")

    def test_one_gwei(self):
        assert from_wei(10**9, "gwei") == Decimal("1")

    def test_one_wei(self):
        assert from_wei(1, "wei") == Decimal("1")

    def test_zero(self):
        assert from_wei(0, "rbtc") == Decimal("0")

    def test_fractional_result(self):
        result = from_wei(10**17, "rbtc")
        assert result == Decimal("0.1")

    def test_default_unit_is_rbtc(self):
        assert from_wei(10**18) == Decimal("1")

    def test_unknown_unit_raises(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            from_wei(1, "unknown")

    def test_round_trip(self):
        original_wei = 123_456_789_000_000_000
        rbtc_value = from_wei(original_wei, "rbtc")
        back_to_wei = to_wei(rbtc_value, "rbtc")
        assert back_to_wei == original_wei
