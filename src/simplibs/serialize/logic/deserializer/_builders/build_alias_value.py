from typing import Any, TypeVar
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext


def build_alias_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build a `NewType`, a `type` alias or a `TypeVar`: build what it stands for.

    Args:
        data: The serialized data at this location.
        annotation: The `NewType`, `TypeAliasType` or `TypeVar`.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The value built against the underlying annotation.
    """

    # 1. A TypeVar stands for its bound, or for anything
    if isinstance(annotation, TypeVar):
        target = annotation.__bound__ if annotation.__bound__ is not None else Any

    # 2. A NewType wraps a type; a `type X = ...` alias holds one
    elif hasattr(annotation, "__supertype__"):
        target = annotation.__supertype__
    else:
        target = annotation.__value__

    # 3. The same data, the same place
    return context.build(data, target, location)


_DESIGN_NOTES = """
# build_alias_value — A Name for Another Annotation

## Purpose
`UserId = NewType("UserId", int)` is an `int` in the data; `type Tree = ...`
(Python 3.12+) is whatever it was defined as. The data does not know the name.

## A Handler for the Name Wins
`register_type(UserId, from_func=...)` is found before this builder is reached.
"""
