from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location


def raise_missing_field_error(
    location: Location,
    annotation: Any,
    names: list[str]
) -> NoReturn:
    """Raise DeserializationError when required fields or keys are absent.

    Args:
        location: Where in the data the object sits.
        annotation: The dataclass, `NamedTuple` or `TypedDict`.
        names: The names that are missing.
    """

    # 1. Raise structured DeserializationError wrapping a ValueError
    listed = ", ".join(repr(name) for name in names)
    raise DeserializationError(
        error_name="DESERIALIZE_MISSING_FIELD",
        label=format_location(location),
        value=names,
        problem=f"{describe_annotation(annotation)} is missing the required: {listed}.",
        expected=f"Every field without a default: {listed}.",
        how_to_fix=(
            "Add the missing keys to the data.",
            "Or give the field a default in the class.",
            "A field excluded with serialized_field(exclude=True) needs a default too.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_missing_field_error — A Required Field Is Absent

## Purpose
All missing names at once, instead of the constructor's `TypeError` naming
only the first.
"""
