from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location


def raise_invalid_key_error(
    location: Location,
    annotation: Any,
    key: str
) -> NoReturn:
    """Raise DeserializationError when a key text is not a valid key of the annotated type.

    Args:
        location: Where in the data the mapping sits.
        annotation: The key annotation.
        key: The key as it is in the data.
    """

    # 1. Raise structured DeserializationError wrapping a ValueError
    wanted = describe_annotation(annotation)
    raise DeserializationError(
        error_name="DESERIALIZE_INVALID_KEY",
        label=format_location(location),
        value=key,
        problem=f"The key {key!r} cannot be read as {wanted}.",
        expected=f"A key that is a valid {wanted}, written as text.",
        how_to_fix=("Correct the key in the data, or change the key type of the annotation.",),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_invalid_key_error — A Key That Is Not the Right Kind

## Purpose
`"abc"` as the key of a `dict[int, str]`. Names the key; the location is the
mapping that holds it.
"""
