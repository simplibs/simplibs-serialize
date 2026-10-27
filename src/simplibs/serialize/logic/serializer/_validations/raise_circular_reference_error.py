from typing import Any, NoReturn
# Outers
from ....exceptions import SerializationError
from ..._common_helpers import format_location, Location


def raise_circular_reference_error(
    location: Location,
    obj: Any
) -> NoReturn:
    """Raise SerializationError when a value contains itself.

    Args:
        location: Where in the data the value was met the second time.
        obj: The value that is already being converted.
    """

    # 1. Raise structured SerializationError wrapping a ValueError
    raise SerializationError(
        error_name="SERIALIZE_CIRCULAR_REFERENCE",
        label=format_location(location),
        value=obj,
        problem=(
            f"This '{type(obj).__name__}' contains itself, "
            "directly or through a handler, so it has no end."
        ),
        expected="Data without cycles — a tree, not a loop.",
        how_to_fix=(
            "Remove the reference that leads back (a parent link, for example).",
            "Exclude that field with serialized_field(exclude=True).",
            "Or let a handler write the object as an identifier instead of its content.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_circular_reference_error — A Loop

## Purpose
A `RecursionError` says only that something nested too deep. This card says
which value came back and where.

## The Parent Link
By far the most common cause is a child object that holds its parent. The
second hint is for it: that field is not data.
"""
