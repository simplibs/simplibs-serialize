from typing import Any
from simplibs.validate import validate_call
# Outers
from ...annotations import ToHandler
from ...exceptions import SerializationError
# Inners
from .serialize import serialize


@validate_call
def is_serializable(
    obj: Any,
    *,
    default: ToHandler | None = None,
    allow_nan: bool = False,
) -> bool:
    """Return True if `serialize` would succeed for the object, False if not.

    Args:
        obj: The value to try.
        default: The same fallback `serialize` takes.
        allow_nan: The same switch `serialize` takes.

    Returns:
        True if the object can be serialized, False if it would raise
        `SerializationError`.
    """

    # 1. Run the real thing — a prediction could disagree with it
    try:
        serialize(obj, default=default, allow_nan=allow_nan)
    except SerializationError:
        return False

    # 2. Nothing went wrong
    return True


_DESIGN_NOTES = """
# is_serializable — Ask Before Writing

## Purpose
Check a value before a file is touched or a message is sent, without a
`try/except` around the real call.

## A Real Run, Not a Guess
It performs the full conversion and discards the result. A separate "can it be
done" walk would have to repeat every decision `serialize` makes and would drift
from it with the first change; the cost is one extra pass.

## What It Does Not Hide
Only `SerializationError` means "no". A `ParamError` (a dataclass field with a
broken `metadata` option) is a bug in the code that declares the class, and
passes through.
"""
