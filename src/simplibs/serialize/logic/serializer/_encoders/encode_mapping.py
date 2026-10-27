from collections.abc import Mapping
from typing import Any
# Outers
from ..._common_helpers import Location
from .._classes import SerializeContext
from .._validations import raise_duplicate_key_error
# Inners
from .encode_mapping_key import encode_mapping_key


def encode_mapping(
    obj: Mapping[Any, Any],
    location: Location,
    context: SerializeContext,
) -> dict[str, Any]:
    """Convert any mapping to a dict with text keys.

    Args:
        obj: A dict, OrderedDict, defaultdict, MappingProxyType, ...
        location: Where in the data this value sits.
        context: The state of the current `serialize` call.

    Returns:
        A dict in the insertion order of the mapping.
    """

    # 1. Each key becomes text, each value is converted below that key
    result: dict[str, Any] = {}
    for key, value in obj.items():
        text = encode_mapping_key(key, location, context)

        # 2. `{1: "a", "1": "b"}` would silently lose one of the two
        if text in result:
            raise_duplicate_key_error(location, text)

        result[text] = context.encode(value, (*location, text))

    # 3. Insertion order is preserved
    return result


_DESIGN_NOTES = """
# encode_mapping — Any Mapping to a Dict

## Purpose
`isinstance(obj, dict)` covered only real dicts; a `MappingProxyType` or a
`ChainMap` is data just as much.

## Two Keys, One Text
After conversion `1` and `"1"` are both `"1"`. A plain dict comprehension keeps
the later one and drops the earlier without a word. This is an error instead.
"""
