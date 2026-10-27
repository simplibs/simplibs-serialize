import dataclasses
from collections.abc import Mapping, Sequence, Set, ValuesView
from typing import Any
# Outers
from ..._constants import JSON_PRIMITIVES
from ..._common_helpers import is_named_tuple, Location
from ...registry import find_to_handler
from .._classes import SerializeContext
from .._helpers import to_primitive
from .._validations import raise_unsupported_type_error
# Inners
from .encode_dataclass import encode_dataclass
from .encode_items import encode_items
from .encode_mapping import encode_mapping
from .encode_with_handler import encode_with_handler


def encode_structure(
    obj: Any,
    location: Location,
    context: SerializeContext
) -> Any:
    """Choose the encoder for a value that is not an exact primitive.

    Args:
        obj: The value.
        location: Where in the data this value sits.
        context: The state of the current `serialize` call.

    Returns:
        The JSON-compatible form of the value.
    """

    # 1. A registered or built-in handler, found through the class hierarchy
    handler = find_to_handler(type(obj))
    if handler is not None:
        return encode_with_handler(handler, obj, location, context)

    # 2. A subclass of str / int / float — the plain value inside it
    if isinstance(obj, JSON_PRIMITIVES):
        return context.encode(to_primitive(obj), location)

    # 3. NamedTuple — a dict of its fields, before it is taken for a plain tuple
    if is_named_tuple(obj):
        return context.encode(obj._asdict(), location)

    # 4. Any mapping
    if isinstance(obj, Mapping):
        return encode_mapping(obj, location, context)

    # 5. A dataclass instance (the class itself is not data)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return encode_dataclass(obj, location, context)

    # 6. Any sequence, set or view of dict values
    if isinstance(obj, (Sequence, Set, ValuesView)):
        return encode_items(obj, location, context)

    # 7. The caller's fallback for everything else
    if context.default is not None:
        return encode_with_handler(context.default, obj, location, context)

    # 8. Nothing recognized
    raise_unsupported_type_error(location, obj)


_DESIGN_NOTES = """
# encode_structure — What Kind of Value Is This

## Purpose
The one place where the order of decisions is written down.

## Why This Order
* Handler first: whatever a user registers for their own class wins over the
  general rule for dicts, lists and dataclasses it happens to derive from.
* Primitive subclass before the containers: a `str` is a `Sequence`, and must
  not become a list of characters.
* NamedTuple before sequence: it is a tuple, but its names are data.
* Mapping before sequence and dataclass: it is the broadest rule among the
  structural ones, checked once.
* `default` last: like `json.dumps(default=...)` it is for what nothing else
  knows, never an override of a rule the library already has.

## Not a Fallback to `__dict__`
An unrecognized object is an error — see `serialize`.
"""
