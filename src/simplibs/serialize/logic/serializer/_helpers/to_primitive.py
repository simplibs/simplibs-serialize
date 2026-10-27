from typing import Any


def to_primitive(
    obj: Any
) -> Any:
    """Return the plain `str`, `int` or `float` inside a subclass of one.

    Args:
        obj: An instance of a subclass of `str`, `int` or `float`.

    Returns:
        The exact built-in value.
    """

    # 1. The base class's own conversion — the subclass may override `__str__`,
    #    `__int__` or `__float__`, and the stored value is what is meant
    if isinstance(obj, str):
        return str.__str__(obj)
    if isinstance(obj, int):
        return int.__int__(obj)
    return float.__float__(obj)


_DESIGN_NOTES = """
# to_primitive — The Value Inside a Subclass

## Purpose
`class Name(str)` or `class Port(int)` is just text or a number to JSON.

## Why Not `str(obj)`
`str(obj)` calls the subclass's own `__str__`, which may return something else
entirely (`"Name(abc)"`). The base class's conversion returns the stored value.

## Enums Never Get Here
An enum member is found by its handler first, so a `class Color(str, Enum)` is
written as its value and not as the text of its name.
"""
