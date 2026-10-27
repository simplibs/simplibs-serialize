from typing import Any, get_args
from simplibs.validate import validate
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._helpers import is_rule_like
from .._validations import raise_build_failed_error, raise_rule_failed_error


def build_annotated_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build `Annotated[T, rule, ...]`: build `T`, then check every rule.

    Args:
        data: The serialized data at this location.
        annotation: The `Annotated` annotation.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The value built against `T`, if it satisfies every rule.
    """

    # 1. The first argument is the type, the rest is metadata
    inner, *metadata = get_args(annotation)

    # 2. The value, built against the underlying type
    value = context.build(data, inner, location)

    # 3. Every rule in the metadata is checked; other metadata is not ours
    for item in metadata:
        if not is_rule_like(item):
            continue
        try:
            passed = validate(value, item, return_bool=True)
        except RecursionError:
            raise
        except Exception as caught:
            raise_build_failed_error(location, annotation, caught)
        if not passed:
            raise_rule_failed_error(location, item, value)

    # 4. The value fits the type and every rule
    return value


_DESIGN_NOTES = """
# build_annotated_value — The Type Keeps Its Rules

## Purpose
`simplibs-types` builds its types as `Annotated[int, rule]`. Taking only
the first argument and dropping the rest would let an `int_port` read from a file
accept `-5` and `99999`.

## Rules in the Metadata
A `Rule`, or a plain predicate function, as `validated_type` accepts. A class or
an object that is not callable (a marker, a docstring) is somebody else's
metadata and is skipped.

## Own Card, Not `ValidateError`
A failed rule is a `DeserializationError` with the location and what the rule
requires, so one `except SerializeError` covers a bad file as a whole — and a
union can treat a failed rule as "this member does not fit".

## Recursion Limit
A `RecursionError` is let through unhandled so that excessive nesting always results 
in a clean `DATA_TOO_DEEP` card at the root, regardless of where the limit was hit.
"""
