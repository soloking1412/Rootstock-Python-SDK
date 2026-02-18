import pytest

from rootstock._utils.namehash import label_hash, namehash, normalize_name
from rootstock.exceptions import InvalidDomainError


class TestNormalizeName:
    def test_simple_domain(self):
        assert normalize_name("alice.rsk") == "alice.rsk"

    def test_uppercase_lowered(self):
        assert normalize_name("Alice.RSK") == "alice.rsk"

    def test_trailing_dot_stripped(self):
        assert normalize_name("alice.rsk.") == "alice.rsk"

    def test_whitespace_stripped(self):
        assert normalize_name("  alice.rsk  ") == "alice.rsk"

    def test_empty_string(self):
        assert normalize_name("") == ""

    def test_empty_label_raises(self):
        with pytest.raises(InvalidDomainError):
            normalize_name("alice..rsk")

    def test_non_string_raises(self):
        with pytest.raises(InvalidDomainError):
            normalize_name(123)  # type: ignore[arg-type]

    def test_single_label(self):
        assert normalize_name("rsk") == "rsk"


class TestLabelHash:
    def test_known_label(self):
        result = label_hash("eth")
        assert len(result) == 32
        assert isinstance(result, bytes)

    def test_different_labels_differ(self):
        assert label_hash("alice") != label_hash("bob")

    def test_deterministic(self):
        assert label_hash("rsk") == label_hash("rsk")


class TestNamehash:
    def test_empty_string(self):
        result = namehash("")
        assert result == b"\x00" * 32

    def test_single_label_eth(self):
        result = namehash("eth")
        assert len(result) == 32
        expected = "0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"
        assert result.hex() == expected[2:]

    def test_subdomain(self):
        result = namehash("foo.eth")
        expected = "0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
        assert result.hex() == expected[2:]

    def test_rsk_tld(self):
        result = namehash("rsk")
        assert len(result) == 32
        assert result != b"\x00" * 32

    def test_rsk_subdomain(self):
        result = namehash("alice.rsk")
        assert len(result) == 32
        assert result != namehash("rsk")
        assert result != namehash("bob.rsk")

    def test_trailing_dot(self):
        assert namehash("alice.rsk.") == namehash("alice.rsk")

    def test_case_insensitive(self):
        assert namehash("Alice.RSK") == namehash("alice.rsk")

    def test_deeply_nested(self):
        result = namehash("sub.alice.rsk")
        assert len(result) == 32
        assert result != namehash("alice.rsk")

    def test_empty_label_raises(self):
        with pytest.raises(InvalidDomainError):
            namehash("alice..rsk")
