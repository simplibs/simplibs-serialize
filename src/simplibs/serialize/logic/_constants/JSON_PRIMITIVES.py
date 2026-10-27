from typing import Final


JSON_PRIMITIVES: Final[tuple[type, ...]] = (str, int, float, bool)
"""The classes JSON writes as they are (`None` is handled apart, it has no class to test)."""


_DESIGN_NOTES = """
# JSON_PRIMITIVES — What Needs No Conversion

## Purpose
One definition of "already JSON" for both directions.

## Exact Type, Not `isinstance`
`serialize` compares the exact `type(obj)` with this tuple. `isinstance` would
also let `class Color(str, Enum)` through as a plain string and leave the enum
member in the output instead of its value.
"""
