from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location


def raise_union_ambiguous_error(
    location: Location,
    annotation: Any,
    data: Any,
    matched: list[Any],
) -> NoReturn:
    """Raise DeserializationError when several members fit and none fits exactly.

    Args:
        location: Where in the data the value sits.
        annotation: The union.
        data: The data.
        matched: The members that can all build the data.
    """

    # 1. Raise structured DeserializationError wrapping a TypeError
    fitting = ", ".join(describe_annotation(member) for member in matched)
    raise DeserializationError(
        error_name="DESERIALIZE_UNION_AMBIGUOUS",
        label=format_location(location),
        value=data,
        problem=f"The data fits several members equally well: {fitting}.",
        expected="Data that fits exactly one member, or one that is exactly the data's own type.",
        how_to_fix=(
            "Narrow the union to members that cannot both accept the same data.",
            f"Or register a handler for this exact annotation: register_type({annotation!r}, from_func=...).",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_union_ambiguous_error — A Real Tie

## Purpose
`list[int] | list[str]` for `[]` has no answer in the data. Guessing the first
would work until someone reorders the union.
"""
