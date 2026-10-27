from collections.abc import Mapping
from typing import Any, TypeVar
# Inners
from .is_plain_class import is_plain_class
# Annotations
Handler = TypeVar("Handler")


def find_handler(
    handlers: Mapping[Any, Handler],
    target: Any,
) -> Handler | None:
    """Find the handler for a class or annotation: exact match, then nearest base.

    Args:
        handlers: A handler table (live or built-in).
        target: The class (or subscripted annotation) to find a handler for.

    Returns:
        The handler, or None if neither the target nor any of its base classes
        has one.
    """

    # 1. Exact match — the only kind of match a subscripted annotation can have
    try:
        exact = handlers.get(target)
    except TypeError:
        return None
    if exact is not None:
        return exact

    # 2. Only a real class has a class hierarchy to walk
    if not is_plain_class(target):
        return None

    # 3. The hierarchy is ordered from the most to the least specific class,
    #    so the first registered base is the nearest one
    for base in target.__mro__[1:]:
        inherited = handlers.get(base)
        if inherited is not None:
            return inherited

    # 4. Nothing registered anywhere along the hierarchy
    return None


_DESIGN_NOTES = """
# find_handler — Exact Match, Then the Nearest Base Class

## Purpose
An exact lookup (`TO_HANDLERS.get(type(obj))`) would miss everything whose real class is a subclass of the registered one:
`Path("x")` is a `PosixPath`, a datetime from a library is often a subclass of
`datetime`, and every enum is its own class.

## Why the Hierarchy Order Is Enough
`datetime` derives from `date`. Walking `datetime.__mro__` from the front finds
the `datetime` entry before the `date` one, so no special ordering rule is
needed anywhere.

## Unhashable Annotations
`Annotated[int, <unhashable metadata>]` cannot be a dict key. For a lookup that
simply means "nothing registered", so it returns None instead of raising.
None.
"""
