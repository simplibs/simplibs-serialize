from enum import Enum
from typing import Any, get_args
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._validations import raise_literal_mismatch_error


def build_literal_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build `Literal[...]`: the data must be one of the listed values.

    Args:
        data: The serialized data at this location.
        annotation: The `Literal` annotation.
        location: Where in the data this value sits.
        context: Not used; builders share one signature.

    Returns:
        The listed value the data equals (an enum member, if the literal lists one).
    """

    # 1. The same type and an equal value — `True` is not `1`
    for allowed in get_args(annotation):
        candidate = allowed.value if isinstance(allowed, Enum) else allowed
        if type(data) is type(candidate) and data == candidate:
            return allowed

    # 2. Not one of the listed values
    raise_literal_mismatch_error(location, annotation, data)


_DESIGN_NOTES = """
# build_literal_value — One of These Values

## Purpose
`Literal["debug", "info"]` — a closed set of values, the usual shape of an
option in a config file.

## Same Type, Equal Value
Python says `True == 1` and `1.0 == 1`. For data that means different things,
so the type has to match too.

## Enum Members
`Literal[Color.RED]` is matched by the member's value, as it is written, and
the member is returned.
"""
