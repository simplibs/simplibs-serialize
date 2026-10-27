# >>> src/simplibs/serialize/logic/serializer/serialize.py
from typing import Any
from simplibs.validate import validate_call
# Outers
from ...annotations import ToHandler
# Inners
from ._classes import SerializeContext
from ._encoders import encode_value
from ._validations import raise_too_deep_error


@validate_call
def serialize(
    obj: Any,
    *,
    default: ToHandler | None = None,
    allow_nan: bool = False,
) -> Any:
    """Convert a Python object into a structure `json.dumps` accepts.

    Args:
        obj: The value to convert.
        default: Called as `default(obj)` for an object nothing else knows how
            to convert. Its result is converted again. Without it such an
            object is an error.
        allow_nan: If True, `nan` and `inf` pass through. They are not valid
            JSON, so by default they are an error.

    Returns:
        A structure made only of `None`, `bool`, `int`, `float`, `str`, `list`
        and `dict`.

    Raises:
        SerializationError: For an unsupported type, a circular reference, a
            non-finite number, two entries under one key, a key that cannot
            be text, a failing handler, or nesting that never ends.
        ParamError: For a dataclass field with invalid `metadata` options.

    Supported: primitives, `list`, `tuple`, `set`, `frozenset` and any other
    sequence or set, any mapping, dataclass instances, `NamedTuple`s, every
    enum, and the types built in or registered with `register_type()`.
    """

    # 1. Everything one call needs is carried in one object
    context = SerializeContext(
        default=default,
        allow_nan=allow_nan,
        encode_value=encode_value,
    )

    # 2. Convert from the root; a loop that never ends becomes a readable card
    try:
        return context.encode(obj, ())
    except RecursionError:
        raise_too_deep_error()


_DESIGN_NOTES = """
# serialize — Python Object to JSON-Compatible Structure

## Purpose
The way out. It does no I/O and writes no text: it returns a structure, and
`to_json` / `dump_json_file` write it.

## Why No `__dict__` or `str()` Fallback
An object that is not understood is an error, never a guess. Writing
`str(obj)` for it would save a file that can never be read back. `default=` is
the explicit, visible way to ask for a fallback.

## `RecursionError`
Caught only here, at the top: a handler chain or a nesting deeper than the
interpreter allows cannot be located exactly, but it can be named.
"""
