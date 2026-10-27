from typing import NoReturn
# Outers
from ....exceptions import SerializationError


def raise_too_deep_error() -> NoReturn:
    """Raise SerializationError when the structure is nested beyond what the interpreter allows."""

    # 1. Raise structured SerializationError wrapping a ValueError
    raise SerializationError(
        error_name="SERIALIZE_TOO_DEEP",
        label="obj",
        problem="The structure is nested too deep to convert.",
        expected="A structure of reasonable depth, without loops.",
        how_to_fix=(
            "Check for a handler that keeps returning a value of its own type.",
            "Check for an object that reaches itself only through a handler.",
            "Flatten extremely deep data before serializing it.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_too_deep_error — The Interpreter's Limit

## Purpose
The circular-reference guard finds a value that contains itself. It cannot find
a handler that makes a new value every time (`lambda o: Wrapper(o)`): each is
different, and the loop never repeats an id. Python's own limit stops it, and
this card is how it is reported.

## No Location
The stack is already gone when the limit is caught, so the card can only name
the whole call.
"""
