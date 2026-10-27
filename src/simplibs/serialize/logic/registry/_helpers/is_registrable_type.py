from typing import Any, get_origin
# Inners
from .is_plain_class import is_plain_class


def is_registrable_type(
    target: Any
) -> bool:
    """Return True if a handler can be registered for the target.

    Args:
        target: The `type_` given to `register_type`.

    Returns:
        True for a class, a subscripted annotation (`list[int]`,
        `Annotated[...]`, `int | None`) or a `NewType`.
    """

    # 1. A real class
    if is_plain_class(target):
        return True

    # 2. A subscripted annotation
    if get_origin(target) is not None:
        return True

    # 3. A NewType: a callable that remembers the type it wraps
    return callable(target) and hasattr(target, "__supertype__")


_DESIGN_NOTES = """
# is_registrable_type — What the Lookup Can Ever Meet

## Purpose
`deserialize` looks handlers up by what the caller wrote as the target type, so
the only keys that can ever match are the things a caller writes there. A string
or an instance stored as a key would never be found; this check refuses it at
the door instead.
"""
