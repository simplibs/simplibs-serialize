from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location


def raise_build_failed_error(
    location: Location,
    annotation: Any,
    caught: Exception
) -> NoReturn:
    """Raise DeserializationError when a handler or a constructor raised.

    Args:
        location: Where in the data the value sits.
        annotation: What was being built.
        caught: The exception that was raised; it becomes the cause.
    """

    # 1. Raise structured DeserializationError wrapping a ValueError, original as cause
    wanted = describe_annotation(annotation)
    raise DeserializationError(
        error_name="DESERIALIZE_BUILD_FAILED",
        label=format_location(location),
        problem=f"Building {wanted} failed: {type(caught).__name__}: {caught}",
        expected=f"Data that {wanted} can be built from.",
        how_to_fix=(
            "Correct the data at this location.",
            "If the type is your own: check its handler or constructor. "
            "The original exception is attached as the cause.",
        ),
        exception=ValueError,
    ) from caught


_DESIGN_NOTES = """
# raise_build_failed_error — Something Refused the Data

## Purpose
`datetime.fromisoformat(5)`, `Color("purple")`, a `__post_init__` that raises,
`set([[1]])`: each is a bare exception from deep inside, with no word about
where in the data it happened. One card puts the location and the type on it
and keeps the original as the cause.
"""
