import math
from typing import Any
# Outers
from ..._constants import JSON_PRIMITIVES
from ..._common_helpers import Location
from .._classes import SerializeContext
from .._validations import raise_circular_reference_error, raise_non_finite_number_error
# Inners
from .encode_structure import encode_structure


def encode_value(
    obj: Any,
    location: Location,
    context: SerializeContext
) -> Any:
    """Convert one value: primitives directly, anything else through the guard.

    Args:
        obj: The value.
        location: Where in the data this value sits.
        context: The state of the current `serialize` call.

    Returns:
        The JSON-compatible form of the value.
    """

    # 1. None needs nothing
    if obj is None:
        return None

    # 2. Exact primitives pass through; only a float can be wrong
    kind = type(obj)
    if kind in JSON_PRIMITIVES:
        if kind is float and not context.allow_nan and not math.isfinite(obj):
            raise_non_finite_number_error(location, obj)
        return obj

    # 3. A value that is already being converted further up is a circle
    identity = id(obj)
    if identity in context.ancestors:
        raise_circular_reference_error(location, obj)

    # 4. Convert, and always leave the path again — the same object may
    #    appear twice side by side, only inside itself is it a circle
    context.ancestors.add(identity)
    try:
        return encode_structure(obj, location, context)
    finally:
        context.ancestors.discard(identity)


_DESIGN_NOTES = """
# encode_value — The Door of Every Value

## Purpose
The hot path: most values in real data are `str`, `int`, `float`, `bool` or
`None`, and they leave in a few comparisons without ever reaching a lookup.

## Exact Type
`type(obj) in JSON_PRIMITIVES` rejects subclasses on purpose; they take the
structure path, where a registered handler (`Enum`) is found before anything
treats them as plain text.

## The Guard Lives Here Only
One place adds an id on the way in and removes it on the way out, so no encoder
has to remember to. A shared reference — one list used in two places — is fine;
only an object that contains itself, directly or through a handler, is a circle.
"""
