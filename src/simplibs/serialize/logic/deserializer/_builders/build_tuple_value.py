import typing
from typing import Any, get_args, get_origin
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._validations import raise_wrong_length_error, raise_wrong_type_error


def build_tuple_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> tuple:
    """Build a tuple from a list.

    Args:
        data: The serialized data — a list.
        annotation: Bare `tuple`, `tuple[T, ...]` or `tuple[A, B, C]`.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The tuple, every item built against its own annotation.
    """

    # 1. A JSON array
    if not isinstance(data, (list, tuple)):
        raise_wrong_type_error(location, annotation, data)

    # 2. The annotation's arguments; `tuple[()]` has none and means "empty"
    args = get_args(annotation)
    bare = get_origin(annotation) is None or annotation is typing.Tuple

    # 3. Bare, or `tuple[T, ...]` — any length, one annotation for all
    if bare or (len(args) == 2 and args[1] is Ellipsis):
        item_annotation = Any if bare else args[0]
        return tuple(
            context.build(item, item_annotation, (*location, index))
            for index, item in enumerate(data)
        )

    # 4. `tuple[A, B, C]` — exactly that many, one annotation per position
    if len(data) != len(args):
        raise_wrong_length_error(location, annotation, data, len(args), len(args))
    return tuple(
        context.build(item, item_annotation, (*location, index))
        for index, (item, item_annotation) in enumerate(zip(data, args))
    )


_DESIGN_NOTES = """
# build_tuple_value — Three Shapes of Tuple

## Purpose
`tuple` means three different things: any tuple, a tuple of one repeated type,
and a tuple of fixed positions.

## The Empty Tuple
`tuple[()]` is a tuple that must be empty; it has no arguments, like bare
`tuple`, and only the missing origin tells them apart.
"""
