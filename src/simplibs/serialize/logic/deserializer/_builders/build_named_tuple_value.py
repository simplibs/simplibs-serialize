from collections.abc import Mapping
from typing import Any, get_origin
# Outers
from ....exceptions import SerializeError
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._helpers import resolve_type_hints
from .._validations import (
    raise_build_failed_error,
    raise_missing_field_error,
    raise_unknown_field_error,
    raise_wrong_length_error,
    raise_wrong_type_error,
)


def build_named_tuple_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build a `NamedTuple` from an object (by name) or from a list (by position).

    Args:
        data: The serialized data — an object keyed by field name, or a list.
        annotation: The `NamedTuple` class.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        An instance of the `NamedTuple`.
    """

    # 1. The class, its fields and defaults, and the type of every field
    cls = annotation if get_origin(annotation) is None else get_origin(annotation)
    names: tuple[str, ...] = cls._fields
    defaults: dict[str, Any] = getattr(cls, "_field_defaults", {})
    try:
        hints = resolve_type_hints(annotation)
    except RecursionError:
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)

    # 2. An object — fields by name, the way `serialize` writes them
    kwargs: dict[str, Any] = {}
    if isinstance(data, Mapping):
        missing = [name for name in names if name not in data and name not in defaults]
        unknown = sorted((key for key in data if key not in names), key=str)
        if context.strict and unknown:
            raise_unknown_field_error(location, annotation, unknown, missing)
        if missing:
            raise_missing_field_error(location, annotation, missing)
        for name in names:
            if name in data:
                kwargs[name] = context.build(data[name], hints.get(name, Any), (*location, name))

    # 3. A list — fields by position
    elif isinstance(data, (list, tuple)):
        required = len([name for name in names if name not in defaults])
        if not required <= len(data) <= len(names):
            raise_wrong_length_error(location, annotation, data, required, len(names))
        for index, item in enumerate(data):
            kwargs[names[index]] = context.build(
                item, hints.get(names[index], Any), (*location, index),
            )

    # 4. Neither
    else:
        raise_wrong_type_error(location, annotation, data)

    # 5. Construct
    try:
        return cls(**kwargs)
    except (SerializeError, RecursionError):
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)


_DESIGN_NOTES = """
# build_named_tuple_value — Names or Positions

## Purpose
`serialize` writes a `NamedTuple` as an object (names are data); files written
by hand or by other tools often use a plain list. Both are read.

## Defaults
A field with a default may be absent, from the right end of a list or anywhere
in an object.

## `collections.namedtuple`
Has no type hints, so every field is `Any`.

## Recursion Limit
A `RecursionError` is let through unhandled so that excessive nesting always results 
in a clean `DATA_TOO_DEEP` card at the root, regardless of where the limit was hit.
"""
