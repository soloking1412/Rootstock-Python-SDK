"""Wei/RBTC unit conversions."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

UNITS: dict[str, int] = {
    "wei": 1,
    "kwei": 10**3,
    "mwei": 10**6,
    "gwei": 10**9,
    "szabo": 10**12,
    "finney": 10**15,
    "ether": 10**18,
    "rbtc": 10**18,
}


def to_wei(value: int | float | str | Decimal, unit: str = "rbtc") -> int:
    unit_lower = unit.lower()
    if unit_lower not in UNITS:
        raise ValueError(f"Unknown unit: {unit!r}. Supported: {', '.join(sorted(UNITS))}")

    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Invalid value: {value!r}") from exc

    result = d * UNITS[unit_lower]
    if result != int(result):
        raise ValueError(
            f"Conversion of {value} {unit} results in fractional Wei ({result}). "
            "Use a smaller unit or adjust the value."
        )
    return int(result)


def from_wei(value: int, unit: str = "rbtc") -> Decimal:
    unit_lower = unit.lower()
    if unit_lower not in UNITS:
        raise ValueError(f"Unknown unit: {unit!r}. Supported: {', '.join(sorted(UNITS))}")

    return Decimal(str(value)) / Decimal(str(UNITS[unit_lower]))
