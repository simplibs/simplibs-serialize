import json
from typing import Any
from simplibs.validate import validate_call
# Outers
from ...annotations import ToHandler
from ..serializer import serialize


@validate_call
def to_json(
    obj: Any,
    *,
    indent: int | str | None = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    allow_nan: bool = False,
    default: ToHandler | None = None,
) -> str:
    """Convert an object to JSON text.

    Args:
        obj: The object to write.
        indent: Indentation: a number of spaces, a string such as `"\\t"`, or
            None for compact one-line output.
        ensure_ascii: If False (default), non-ASCII text is written as it is
            (`č`, not `\\u010d`).
        sort_keys: If True, object keys are sorted — reproducible output.
        allow_nan: If False (default), `NaN` and `Infinity` are an error, because
            they are not valid JSON.
        default: The fallback for an object nothing else can convert; see
            `serialize`.

    Returns:
        The JSON text (without a trailing newline).

    Raises:
        SerializationError: As for `serialize`.
    """

    # 1. Convert to a structure first — anything wrong is found here, with its location
    structure = serialize(obj, default=default, allow_nan=allow_nan)

    # 2. Write it as text; a structure `serialize` made cannot fail here
    return json.dumps(
        structure,
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        allow_nan=allow_nan,
    )


_DESIGN_NOTES = """
# to_json — Object to JSON Text
## `sort_keys` Is Safe Here
`json.dumps(sort_keys=True)` fails on a dict with keys of mixed types. After
`serialize` every key is text, so it cannot fail.

## No Trailing Newline
A string is a value; the newline belongs to a file, and `dump_json_file` adds it.
"""
