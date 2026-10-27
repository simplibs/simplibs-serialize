from typing import NoReturn
# Outers
from ....exceptions import DeserializationError


def raise_data_too_deep_error() -> NoReturn:
    """Raise DeserializationError when the data is nested beyond what the interpreter allows."""

    # 1. Raise structured DeserializationError wrapping a ValueError
    raise DeserializationError(
        error_name="DESERIALIZE_DATA_TOO_DEEP",
        label="data",
        problem="The data is nested too deep to build.",
        expected="Data of reasonable depth.",
        how_to_fix=(
            "Check where the data comes from — real data is rarely a thousand levels deep.",
            "Flatten extremely deep data before deserializing it.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_data_too_deep_error — The Interpreter's Limit

## Purpose
Data cannot be a cycle, but it can be hostile: a file nested a hundred thousand
levels would crash a program with a bare `RecursionError`. The card is the polite
version, and the only way it can be raised is from the top of `deserialize`.
"""
