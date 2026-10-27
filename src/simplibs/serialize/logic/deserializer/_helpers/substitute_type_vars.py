from collections.abc import Mapping
from typing import Any, TypeVar


def substitute_type_vars(
    hint: Any,
    mapping: Mapping[Any, Any]
) -> Any:
    """Replace the type variables inside one annotation.

    Args:
        hint: An annotation: `T`, `list[T]`, `T | None`, `Annotated[T, ...]`, `int`.
        mapping: Type variable → what it stands for.

    Returns:
        The annotation with its type variables replaced; a variable that is not
        in the mapping becomes its bound, or `Any`.
    """

    # 1. The variable itself
    if isinstance(hint, TypeVar):
        if hint in mapping:
            return mapping[hint]
        return hint.__bound__ if hint.__bound__ is not None else Any

    # 2. A subscripted annotation that contains variables is subscripted again
    parameters = getattr(hint, "__parameters__", ())
    if parameters and not isinstance(hint, type):
        return hint[tuple(substitute_type_vars(parameter, mapping) for parameter in parameters)]

    # 3. Nothing to replace
    return hint


_DESIGN_NOTES = """
# substitute_type_vars — T Becomes int

## Purpose
`Box[int]` says what `T` is once; every field that mentions `T` — directly or
inside `list[T]`, `T | None`, `Annotated[T, rule]` — has to hear it.

## Why Subscripting Works
A generic alias knows its own parameters (`list[T].__parameters__ == (T,)`) and
`list[T][int]` is `list[int]` — Python does the substitution; this only supplies
the values.
"""
