from collections.abc import Callable
from typing import Any
# Outers
from ....exceptions import SerializeError
from ..._common_helpers import Location
from .._validations import raise_build_failed_error


def build_with_handler(
    handler: Callable[[Any, Any], Any],
    data: Any,
    annotation: Any,
    location: Location,
) -> Any:
    """Call a registered `from_func` and wrap whatever it raises.

    Args:
        handler: The `from_func(data, annotation)`.
        data: The serialized data at this location.
        annotation: The annotation the handler was found for.
        location: Where in the data this value sits.

    Returns:
        What the handler built.
    """

    # 1. A handler is not a guard: a number where a date string belongs is a
    #    TypeError in there. It becomes one card with a location
    try:
        return handler(data, annotation)
    except (SerializeError, RecursionError):
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)


_DESIGN_NOTES = """
# build_with_handler — One Handler Call

## Purpose
The built-in handlers are one-line lambdas that do not check their input. This
is the single place that does, by catching what they raise — written once
instead of in every lambda.

## Which Errors Pass Through
`SerializeError` (a handler that itself calls `deserialize`) is already a card;
`RecursionError` is handled at the top of `deserialize`.
"""
