from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location


def raise_unknown_field_error(
    location: Location,
    annotation: Any,
    unknown: list[Any],
    missing: list[str],
) -> NoReturn:
    """Raise DeserializationError when strict data has keys the class does not have.

    Args:
        location: Where in the data the object sits.
        annotation: The dataclass, `NamedTuple` or `TypedDict`.
        unknown: The keys the class does not have.
        missing: The required names that are absent — often the same mistake.
    """

    # 1. Raise structured DeserializationError wrapping a ValueError
    listed = ", ".join(repr(name) for name in unknown)
    hint = ""
    if missing:
        hint = f" Required but absent: {', '.join(repr(name) for name in missing)} — a misspelled name?"
    raise DeserializationError(
        error_name="DESERIALIZE_UNKNOWN_FIELD",
        label=format_location(location),
        value=unknown,
        problem=f"{describe_annotation(annotation)} has no such key: {listed}.{hint}",
        expected="Only the keys the class defines (under their alias, if it has one).",
        how_to_fix=(
            "Remove or rename the unknown keys.",
            "Or pass strict=False to deserialize() to ignore them.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_unknown_field_error — A Key Nobody Asked For

## Purpose
Strict by default, because the usual cause is a typo, and a typo silently
ignored leaves a setting at its default while the file says otherwise.

## Missing Together With Unknown
`usernmae` unknown and `username` missing are one mistake; the card shows both.
"""
