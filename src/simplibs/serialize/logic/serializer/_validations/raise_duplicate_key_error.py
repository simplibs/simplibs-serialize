from typing import NoReturn
# Outers
from ....exceptions import SerializationError
from ..._common_helpers import format_location, Location


def raise_duplicate_key_error(
    location: Location,
    key: str
) -> NoReturn:
    """Raise SerializationError when two entries would be written under one key.

    Args:
        location: Where in the data the mapping or dataclass sits.
        key: The key that would be used twice.
    """

    # 1. Raise structured SerializationError wrapping a ValueError
    raise SerializationError(
        error_name="SERIALIZE_DUPLICATE_KEY",
        label=format_location(location),
        value=key,
        problem=f"Two entries would be written under the key {key!r}; one would be lost.",
        expected="Keys that stay different after conversion to text.",
        how_to_fix=(
            "In a dict: do not mix keys such as 1 and '1' — they are the same text.",
            "In a dataclass: give the fields different aliases.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_duplicate_key_error — One Key, Two Values

## Purpose
Silently dropping one of the two values is data loss without a trace. Both
sources of it (`{1: .., "1": ..}` and two equal aliases) end here.
"""
