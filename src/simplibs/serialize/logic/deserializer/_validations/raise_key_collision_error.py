from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import format_location, Location


def raise_key_collision_error(
    location: Location,
    key: Any,
    first: Any,
    second: Any
) -> NoReturn:
    """Raise DeserializationError when two keys of the data become one key of the mapping.

    Args:
        location: Where in the data the mapping sits.
        key: The key both texts were read back as.
        first: The key text that was read first.
        second: The key text that collides with it.
    """
    # 1. Raise structured DeserializationError wrapping a ValueError
    raise DeserializationError(
        error_name="DESERIALIZE_KEY_COLLISION",
        label=format_location(location),
        value=second,
        problem=f"The keys {first!r} and {second!r} both stand for {key!r}; one value would be lost.",
        expected="Keys that stay different after they are read back.",
        how_to_fix=(
            "Remove one of the two entries from the data.",
            "Or annotate the keys as `str`, which keeps the text as it is.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_key_collision_error — Two Keys, One Key

## Purpose
`"1.0"` and `"1.00"` are two keys of a JSON object but one `float` key once read back.
Silently keeping the last one would lose data without a word — the same mistake
`raise_duplicate_key_error` prevents on the way out.

## Logic
Raised by `build_mapping_value` when a built key is already in the result.
`value` is the second key text, `label` the location of the mapping.
"""
