from collections.abc import Mapping
from typing import Any, get_origin
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._helpers import resolve_type_hints
from .._validations import (
    raise_build_failed_error,
    raise_missing_field_error,
    raise_unknown_field_error,
    raise_wrong_type_error,
)


def build_typed_dict_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> dict[str, Any]:
    """Build a `TypedDict` from an object, each key against its own type.

    Args:
        data: The serialized data — an object.
        annotation: The `TypedDict` class.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        A dict with the keys that were present, each value built.
    """

    # 1. A JSON object
    if not isinstance(data, Mapping):
        raise_wrong_type_error(location, annotation, data)

    # 2. The class, its required keys and the type of every key
    cls = annotation if get_origin(annotation) is None else get_origin(annotation)
    required: frozenset[str] = cls.__required_keys__
    try:
        hints = resolve_type_hints(annotation)
    except RecursionError:
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)

    # 3. A missing required key and an unknown key are both reported
    missing = sorted(key for key in required if key not in data)
    unknown = sorted((key for key in data if key not in hints), key=str)
    if context.strict and unknown:
        raise_unknown_field_error(location, annotation, unknown, missing)
    if missing:
        raise_missing_field_error(location, annotation, missing)

    # 4. Every key that is present is built
    return {
        key: context.build(data[key], hint, (*location, key))
        for key, hint in hints.items()
        if key in data
    }


_DESIGN_NOTES = """
# build_typed_dict_value — A Dict With a Schema

## Purpose
`TypedDict` is the schema of a dict that stays a dict; the result is a plain
`dict`, as a `TypedDict` is at run time.

## Required and Optional
`__required_keys__` already accounts for `total=False`, `Required` and
`NotRequired`; the qualifiers inside the hints are removed by the
`build_qualified_value` builder when each key is built.

## Recursion Limit
A `RecursionError` is let through unhandled so that excessive nesting always results 
in a clean `DATA_TOO_DEEP` card at the root, regardless of where the limit was hit.
"""
