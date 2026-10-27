from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location
from .._helpers import name_json_type


def raise_wrong_type_error(
    location: Location,
    annotation: Any,
    data: Any
) -> NoReturn:
    """Raise DeserializationError when the data is another kind than the annotation needs.

    Args:
        location: Where in the data the value sits.
        annotation: What the data should have been.
        data: What was there.
    """

    # 1. Raise structured DeserializationError wrapping a TypeError
    wanted = describe_annotation(annotation)
    raise DeserializationError(
        error_name="DESERIALIZE_WRONG_TYPE",
        label=format_location(location),
        value=data,
        problem=f"Got {name_json_type(data)}, but the data should be {wanted}.",
        expected=wanted,
        how_to_fix=("Correct the data at this location so that it has the shape the type needs.",),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_wrong_type_error — Right Place, Wrong Kind of Value

## Purpose
The most common card: a text where a number belongs, `null` for a required
value, an object where a list was expected.
"""
