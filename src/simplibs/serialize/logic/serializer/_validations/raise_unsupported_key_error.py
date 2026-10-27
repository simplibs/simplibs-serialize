from typing import Any, NoReturn
# Outers
from ....exceptions import SerializationError
from ..._common_helpers import format_location, Location


def raise_unsupported_key_error(
    location: Location,
    key: Any
) -> NoReturn:
    """Raise SerializationError when a mapping key cannot be written as text.

    Args:
        location: Where in the data the mapping sits.
        key: The key that cannot be converted.
    """

    # 1. Raise structured SerializationError wrapping a TypeError
    raise SerializationError(
        error_name="SERIALIZE_UNSUPPORTED_KEY",
        label=format_location(location),
        value=key,
        problem=f"The key {key!r} ('{type(key).__name__}') has no text form.",
        expected="A key that is text, a number, a bool, None, or converts to text (enum, date, UUID, ...).",
        how_to_fix=(
            "Use text keys, for example '1,2' instead of the tuple (1, 2).",
            "Or turn the mapping into a list of {'key': ..., 'value': ...} entries before serializing.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_unsupported_key_error — A Key Has to Be Text

## Purpose
JSON has no other kind of key. A tuple key has no single honest text, so
guessing one (`"(1, 2)"`) would only make the file unreadable for the way back.
"""
