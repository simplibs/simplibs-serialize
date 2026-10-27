from typing import Any, get_args, get_origin
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._validations import raise_build_failed_error, raise_wrong_type_error
# Inners
from .constants import ELEMENT_FACTORIES


def build_elements_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build a list, set, frozenset, deque or abstract collection from a list.

    Args:
        data: The serialized data — a list.
        annotation: `list[int]`, `set[str]`, `Sequence[Point]`, bare `list`, ...
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The container, each item built against the item annotation (`Any` if
        the annotation gives none).
    """

    # 1. JSON has an array for all of these; text is not an array of characters
    if not isinstance(data, (list, tuple)):
        raise_wrong_type_error(location, annotation, data)

    # 2. The item annotation, if there is one
    args = get_args(annotation)
    item_annotation = args[0] if args else Any

    # 3. Every item, with its index in the location
    items = [
        context.build(item, item_annotation, (*location, index))
        for index, item in enumerate(data)
    ]

    # 4. The container the annotation asks for — a set can refuse unhashable items
    factory = ELEMENT_FACTORIES.get(get_origin(annotation) or annotation, list)
    try:
        return factory(items)
    except RecursionError:
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)


_DESIGN_NOTES = """
# build_elements_value — A List Becomes the Container

## Purpose
One builder for everything made of items: `list`, `set`, `frozenset`, `deque`,
`Sequence`, `Iterable`, `Collection`, ...

## Duplicates in a Set
`[1, 1]` as `set[int]` is `{1}`. A set cannot hold two, and the library does not
refuse data it could read.

## Recursion Limit
A `RecursionError` is let through unhandled so that excessive nesting always results 
in a clean `DATA_TOO_DEEP` card at the root, regardless of where the limit was hit.
"""
