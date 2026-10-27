from typing import Any
# Outers
from ..._common_helpers import Location
from .._classes import SerializeContext
from .._validations import raise_unsupported_key_error


def encode_mapping_key(
    key: Any,
    location: Location,
    context: SerializeContext
) -> str:
    """Convert one dictionary key to the text a JSON object needs.

    Args:
        key: The key as it is in the Python mapping.
        location: The location of the mapping (the key is not part of it yet).
        context: The state of the current `serialize` call.

    Returns:
        The key as text.
    """

    # 1. A text key is already what is needed
    if type(key) is str:
        return key

    # 2. Any other key is converted like a value — an enum gives its value,
    #    a date its ISO text, a UUID its text
    encoded = context.encode(key, location)

    # 3. Text stays text
    if isinstance(encoded, str):
        return encoded

    # 4. Scalars are written the way `json.dumps` writes them (bool before int)
    if encoded is None:
        return "null"
    if isinstance(encoded, bool):
        return "true" if encoded else "false"
    if isinstance(encoded, (int, float)):
        return repr(encoded)

    # 5. A list or a dict (for example a tuple) cannot be a key
    raise_unsupported_key_error(location, key)


_DESIGN_NOTES = """
# encode_mapping_key — A Key Is Always Text

## Purpose
JSON objects have text keys only. A plain `str(key)` would produce `"Color.RED"` for
an enum, `"None"` for `None` and `"2024-01-02 00:00:00"` for a datetime — texts
nobody could turn back into the key.

## Same Rules as `json.dumps`
`1` → `"1"`, `1.5` → `"1.5"`, `True` → `"true"`, `None` → `"null"`. Reading the
data back, a key is parsed from exactly these texts when the annotation says
`dict[int, ...]`, `dict[bool, ...]` and so on.

## A Tuple Is Not a Key
`{(1, 2): "a"}` has no honest text form. It is an error with the key named, and
the way out is to give the dict text keys.
"""
