from typing import Any
# Outers
from ...annotations import ToHandler
# Inners
from ._handlers.active import TO_HANDLERS
from ._helpers import find_handler


def find_to_handler(
    type_: Any
) -> ToHandler | None:
    """Find the handler `serialize` uses for objects of a class.

    Args:
        type_: The class of the object, i.e. `type(obj)`.

    Returns:
        The handler registered for the class or for its nearest base class,
        or None.
    """

    # 1. Look the class up in the live table
    return find_handler(TO_HANDLERS, type_)


_DESIGN_NOTES = """
# find_to_handler — The Handler for an Object

## Purpose
The only way `serialize` reaches the registry: it never sees the table itself,
so nothing in the core can change it by accident.
"""
