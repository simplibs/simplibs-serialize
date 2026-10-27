import dataclasses
from collections.abc import Mapping
from typing import Any, get_origin
# Outers
from ....exceptions import SerializeError
from ..._common_helpers import get_field_options, Location
from .._classes import DeserializeContext
from .._helpers import has_default, resolve_type_hints
from .._validations import (
    raise_build_failed_error,
    raise_missing_field_error,
    raise_unknown_field_error,
    raise_wrong_type_error,
)


def build_dataclass_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build a dataclass instance from an object, each field against its own type.

    Args:
        data: The serialized data — an object keyed by the names in the data.
        annotation: The dataclass, or a generic one such as `Box[int]`.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        An instance of the dataclass.
    """

    # 1. A JSON object
    if not isinstance(data, Mapping):
        raise_wrong_type_error(location, annotation, data)

    # 2. The class and the real type of every field (forward references and
    #    type variables resolved, `Annotated` kept so that its rules run)
    cls = annotation if get_origin(annotation) is None else get_origin(annotation)
    try:
        hints = resolve_type_hints(annotation)
    except RecursionError:
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)

    # 3. Each field: its name in the data, whether it is data at all, its value
    kwargs: dict[str, Any] = {}
    known: set[str] = set()
    missing: list[str] = []
    for field in dataclasses.fields(cls):
        name, exclude = get_field_options(field)

        # 3.1 A derived field (`init=False`) may be in the data; it is never passed in
        if not field.init:
            known.add(name)
            continue

        # 3.2 An excluded field is not data — it must come from its default
        if exclude:
            if not has_default(field):
                missing.append(field.name)  # an excluded field is never in the data: only its attribute name exists
            continue

        # 3.3 A present field is built; an absent one needs a default
        known.add(name)
        if name in data:
            kwargs[field.name] = context.build(
                data[name], hints.get(field.name, Any), (*location, name),
            )
        elif not has_default(field):
            missing.append(name)

    # 4. Unknown keys (strict) are reported first: they often explain a missing field
    if context.strict:
        unknown = sorted((key for key in data if key not in known), key=str)
        if unknown:
            raise_unknown_field_error(location, annotation, unknown, missing)
    if missing:
        raise_missing_field_error(location, annotation, missing)

    # 5. Construct — the class may refuse (a `__post_init__`, `validate_dataclass`)
    try:
        return cls(**kwargs)
    except (SerializeError, RecursionError):
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)


_DESIGN_NOTES = """
# build_dataclass_value — An Object Becomes a Dataclass

## Purpose
Every field is built against its own type, found under its name in the data.

## Excluded Without a Default
Such a field can never be built; it is reported as missing, and the card says
why.

## A Rejecting Constructor
A `validate_dataclass` class or a `__post_init__` that raises ends as a card
with the location; its own exception is the cause.

## Recursion Limit
A `RecursionError` is let through unhandled so that excessive nesting always results 
in a clean `DATA_TOO_DEEP` card at the root, regardless of where the limit was hit.
"""
