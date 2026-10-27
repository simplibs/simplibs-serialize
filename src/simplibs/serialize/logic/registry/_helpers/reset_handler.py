from collections.abc import Mapping, MutableMapping
from typing import Any


def reset_handler(
    live: MutableMapping[Any, Any],
    builtin: Mapping[Any, Any],
    key: Any,
) -> bool:
    """Put one entry of a live table back as it was shipped.

    Args:
        live: The live handler table.
        builtin: The built-in table of the same direction.
        key: The class or annotation to reset.

    Returns:
        True if the live table changed, False otherwise.
    """

    # 1. An unhashable key was never registered
    try:
        original = builtin.get(key)
        current = live.get(key)
    except TypeError:
        return False

    # 2. A built-in handler exists — restore it
    if original is not None:
        live[key] = original
        return current is not original

    # 3. Otherwise the entry is purely a registration — remove it
    return live.pop(key, None) is not None


_DESIGN_NOTES = """
# reset_handler — One Entry, One Direction

## Purpose
The part of `unregister_type` that is the same for both tables, written once.

## Why Restore, Not Delete
Deleting the `datetime` entry after someone replaced it would leave the library
unable to handle datetimes at all. The entry returns to what was shipped.
"""
