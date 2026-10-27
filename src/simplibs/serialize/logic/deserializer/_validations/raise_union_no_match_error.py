from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import describe_annotation, format_location, Location
from .._helpers import name_json_type


def raise_union_no_match_error(
    location: Location,
    annotation: Any,
    data: Any,
    closest: DeserializationError | None = None,
) -> NoReturn:
    """Raise DeserializationError when no member of a union fits the data.

    Args:
        location: Where in the data the value sits.
        annotation: The union.
        data: The data that fits no member.
        closest: The failure of the member that got deepest into the data, if any;
            it becomes the cause.
    """

    # 1. Raise structured DeserializationError wrapping a TypeError
    wanted = describe_annotation(annotation)
    raise DeserializationError(
        error_name="DESERIALIZE_UNION_NO_MATCH",
        label=format_location(location),
        value=data,
        problem=f"Got {name_json_type(data)}, which fits none of: {wanted}.",
        expected=f"Data that fits one of: {wanted}.",
        how_to_fix=("Correct the data so that it fits one of the members of the union.",),
        exception=TypeError,
    ) from closest


_DESIGN_NOTES = """
# raise_union_no_match_error — None of the Members

## Purpose
Names the members, so the reader sees what was possible without opening the code.
"""
