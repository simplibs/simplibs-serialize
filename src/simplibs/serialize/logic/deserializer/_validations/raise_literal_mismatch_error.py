from typing import Any, NoReturn, get_args
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import format_location, Location


def raise_literal_mismatch_error(
    location: Location,
    annotation: Any,
    data: Any
) -> NoReturn:
    """Raise DeserializationError when the data is not one of the values of a `Literal`.

    Args:
        location: Where in the data the value sits.
        annotation: The `Literal` annotation.
        data: The data.
    """

    # 1. Raise structured DeserializationError wrapping a ValueError
    allowed = ", ".join(repr(value) for value in get_args(annotation))
    raise DeserializationError(
        error_name="DESERIALIZE_LITERAL_MISMATCH",
        label=format_location(location),
        value=data,
        problem=f"{data!r} is not one of the allowed values.",
        expected=f"One of: {allowed}.",
        how_to_fix=("Use one of the listed values — the type of the value matters (`1` is not `True`).",),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_literal_mismatch_error — Not on the List

## Purpose
Prints the list, so a misspelled option in a config file is fixed from the card.
"""
