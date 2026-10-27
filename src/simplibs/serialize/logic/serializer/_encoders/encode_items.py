from collections.abc import Sequence, Set
from typing import Any
# Outers
from ..._common_helpers import Location
from .._classes import SerializeContext
from .._helpers import sort_items


def encode_items(
    obj: Sequence[Any] | Set[Any],
    location: Location,
    context: SerializeContext,
) -> list[Any]:
    """Convert a sequence or a set to a list.

    Args:
        obj: Any sequence (list, tuple, deque, ...) or set (set, frozenset, ...).
        location: Where in the data this value sits.
        context: The state of the current `serialize` call.

    Returns:
        A list; for a set, in a fixed order.
    """

    # 1. Every item, with its index in the location
    items = [
        context.encode(item, (*location, index))
        for index, item in enumerate(obj)
    ]

    # 2. A set has no order of its own, so it is given one
    if isinstance(obj, Set):
        return sort_items(items)

    # 3. A sequence keeps the order it has
    return items


_DESIGN_NOTES = """
# encode_items — Sequences and Sets to a List

## Purpose
`list`, `tuple`, `deque`, `range`, `set`, `frozenset`, `dict.keys()`, `dict.values()`: one rule,
because JSON has one array.

## Sets in a Fixed Order
The order of a set of strings changes with every interpreter start. Saving the
same data twice would produce two different files and a diff full of nothing.
The items are converted first and sorted afterwards (`sort_items`).

## The Index in a Set's Location
The items of a set are converted first and sorted afterwards, so an index in an error
location is the item's position in the iteration order of the set, not in the sorted
list that is written. For a set that is the only order there is to point at.
"""
