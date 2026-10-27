import typing
from typing import Any, TypeVar

_TypeAliasType = getattr(typing, "TypeAliasType", None)


def is_alias_annotation(
    annotation: Any
) -> bool:
    """Return True for a `NewType`, a `type` alias or a `TypeVar`.

    Args:
        annotation: Anything used as an annotation.
    """

    # 1. A TypeVar
    if isinstance(annotation, TypeVar):
        return True

    # 2. A NewType remembers the type it wraps
    if hasattr(annotation, "__supertype__"):
        return True

    # 3. A `type X = ...` alias — only where the interpreter has them (3.12+)
    return _TypeAliasType is not None and isinstance(annotation, _TypeAliasType)


_DESIGN_NOTES = """
# is_alias_annotation — A Name for Something Else

## Purpose
These three have no `get_origin`; they are recognized by what they are.
"""
