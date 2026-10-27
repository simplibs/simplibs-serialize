import json
from typing import NoReturn
# Outers
from ....exceptions import DeserializationError


def raise_invalid_json_error(
    json_str: str | bytes,
    caught: ValueError | RecursionError
) -> NoReturn:
    """Raise DeserializationError when text cannot be parsed as JSON.

    Args:
        json_str: The text (or bytes) that was parsed.
        caught: The `JSONDecodeError`, `UnicodeDecodeError` or `RecursionError` that was raised;
            it becomes the cause.
    """

    # 1. A syntax error knows where; anything else (bad bytes) only what
    if isinstance(caught, json.JSONDecodeError):
        place = f" at line {caught.lineno}, column {caught.colno}"
        problem = f"The text is not valid JSON{place}: {caught.msg}."
        excerpt = None
        if isinstance(json_str, str):
            excerpt = json_str[max(0, caught.pos - 20):caught.pos + 20]
    elif isinstance(caught, RecursionError):
        problem = "The text is nested so deeply that it cannot be read."
        excerpt = None
    else:
        problem = f"The text could not be read as JSON: {caught}."
        excerpt = None

    # 2. Raise structured DeserializationError wrapping a ValueError, original as cause
    raise DeserializationError(
        error_name="DESERIALIZE_INVALID_JSON",
        label="json_str",
        value=excerpt,
        problem=problem,
        expected="Valid JSON text (UTF-8 if given as bytes).",
        how_to_fix=(
            "Fix the text at the reported position — a missing comma, a trailing comma, "
            "single quotes and unquoted keys are the usual causes.",
            "The value shown is the text around that position.",
        ),
        exception=ValueError,
    ) from caught


_DESIGN_NOTES = """
# raise_invalid_json_error — Where the Text Breaks

## Purpose
`json.JSONDecodeError: Expecting ',' delimiter: line 7 column 3 (char 112)` is
accurate, but it is not a `SerializeError`, so it escapes an `except` meant for a
bad file. The card carries the same line and column, plus about forty characters
around the spot, so the problem is usually visible without opening the file.

## Bytes
Invalid UTF-8 in `bytes` raises `UnicodeDecodeError` inside `json.loads`; it has
no line, only a message, and becomes the same kind of card.
"""
