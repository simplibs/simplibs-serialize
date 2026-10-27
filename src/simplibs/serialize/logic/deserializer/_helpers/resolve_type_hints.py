from typing import Any, get_args, get_origin, get_type_hints
# Inners
from .substitute_type_vars import substitute_type_vars


def resolve_type_hints(
    annotation: Any
) -> dict[str, Any]:
    """Return the real types of the fields of a class, with type variables filled in.

    Args:
        annotation: A dataclass, `NamedTuple` or `TypedDict`, or a parameterized
            generic one such as `Box[int]`.

    Returns:
        Field name → annotation. Forward references are resolved and
        `Annotated` is kept, so that its rules still run.

    Raises:
        Exception: Whatever `typing.get_type_hints` raises for a reference it
            cannot resolve (the caller turns it into a card).
    """

    # 1. The class itself, for `Box[int]` the class `Box`
    origin = get_origin(annotation)
    cls = annotation if origin is None else origin

    # 2. `include_extras` keeps `Annotated[...]`; without it the rules are lost
    hints = get_type_hints(cls, include_extras=True)

    # 3. `Box[int]` fills the type variable `T` of `Box` with `int`
    parameters = getattr(cls, "__parameters__", ())
    mapping = dict(zip(parameters, get_args(annotation) if origin is not None else ()))

    # 4. Every hint with its type variables replaced
    return {name: substitute_type_vars(hint, mapping) for name, hint in hints.items()}


_DESIGN_NOTES = """
# resolve_type_hints — What Each Field Really Is

## Purpose
`field.type` can be a string (`from __future__ import annotations`) and a
forward reference; `get_type_hints` turns both into real types.

## `include_extras=True`
`get_type_hints(cls)` with its default strips `Annotated[T, rule]` to `T`, which
would throw away every rule on every dataclass field.

## Generic Classes
`Box[int]` has a field `item: T`; the hint is `T` until `Box`'s parameters are
matched with `int`. Bare `Box` leaves `T` to its bound, or `Any`.
"""
