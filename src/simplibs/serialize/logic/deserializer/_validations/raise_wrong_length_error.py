from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location


def raise_wrong_length_error(
    location: Location,
    annotation: Any,
    data: Any,
    minimum: int,
    maximum: int,
) -> NoReturn:
    """Raise DeserializationError for a list of the wrong length.

    Args:
        location: Where in the data the list sits.
        annotation: The tuple or `NamedTuple` annotation.
        data: The list.
        minimum: The fewest items allowed.
        maximum: The most items allowed.
    """

    # 1. Raise structured DeserializationError wrapping a ValueError
    wanted = f"{minimum} items" if minimum == maximum else f"{minimum} to {maximum} items"
    raise DeserializationError(
        error_name="DESERIALIZE_WRONG_LENGTH",
        label=format_location(location),
        value=data,
        problem=f"Got {len(data)} items, but {describe_annotation(annotation)} needs {wanted}.",
        expected=wanted,
        how_to_fix=("Add or remove items so that the list has the length the type needs.",),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_wrong_length_error — Too Many or Too Few

## Purpose
`[1, 2, 3]` for `tuple[int, int]` was quietly cut to `(1, 2)`. Now it says so.
"""
