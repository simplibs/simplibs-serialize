from collections.abc import Callable
from typing import Any, TypeAlias


ToHandler: TypeAlias = Callable[[Any], Any]
"""A function `to_func(obj)` that turns an object into a value `serialize` understands."""


_DESIGN_NOTES = """
# ToHandler — The Shape of `to_func`

## Purpose
One name for "the function you pass as `to_func` to `register_type`".

## Result Is Serialized Again
The value a handler returns does not have to be JSON-ready already: it may be
anything `serialize` itself can handle (a `dict` holding datetimes, a dataclass,
an enum member). The returned value goes through `serialize` once more. That is
what lets a handler stay one line long.
"""
