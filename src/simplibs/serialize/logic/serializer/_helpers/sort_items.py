import json
from typing import Any


def sort_items(items: list[Any]) -> list[Any]:
    """Put already converted items of a set in a fixed order.

    Args:
        items: JSON-compatible values.

    Returns:
        A new list: sorted by value if the items can be compared, otherwise
        sorted by their JSON text.
    """

    # 1. Items that can be compared are sorted the natural way — 2 before 10
    try:
        return sorted(items)
    except TypeError:
        pass

    # 2. Mixed or structured items (a dict, None next to a number) are
    #    ordered by their text, which is always defined
    return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))


_DESIGN_NOTES = """
# sort_items — A Set Gets an Order

## Purpose
The same set must produce the same text every time. The order of items in a
`set` depends on hashes, and string hashes change with every interpreter start.

## Two Ways, One Result per Input
Natural order where it exists (numbers by size, text alphabetically), a
fallback by JSON text where it does not. Neither depends on anything random.

## Sorted After Conversion
The items are sorted as converted JSON values, not as the original objects:
`Color.RED` and `Color.BLUE` are ordered by what is written for them.
"""
