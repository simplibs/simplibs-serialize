from typing import Any, NoReturn
# Outers
from ....exceptions import SerializationError
from ..._common_helpers import format_location, Location


def raise_handler_failed_error(
    location: Location,
    obj: Any,
    caught: Exception
) -> NoReturn:
    """Raise SerializationError when a handler raised an exception of its own.

    Args:
        location: Where in the data the value sits.
        obj: The value the handler was called with.
        caught: The exception the handler raised; it becomes the cause.
    """

    # 1. Raise structured SerializationError wrapping a ValueError, original as cause
    raise SerializationError(
        error_name="SERIALIZE_HANDLER_FAILED",
        label=format_location(location),
        value=obj,
        problem=(
            f"The handler for '{type(obj).__name__}' raised "
            f"{type(caught).__name__}: {caught}"
        ),
        expected="A handler that returns a value for every object of its type.",
        how_to_fix=(
            "Fix the handler registered with register_type() (or the `default=` function).",
            "The original exception is attached as the cause of this one.",
        ),
        exception=ValueError,
    ) from caught


_DESIGN_NOTES = """
# raise_handler_failed_error — The Handler Is the Problem

## Purpose
A bare `AttributeError: 'NoneType' has no attribute 'x'` from a lambda in
a registry, three recursion levels deep, says nothing about which value was
being converted. The card adds the location and the type; the cause keeps the
original traceback.
"""
