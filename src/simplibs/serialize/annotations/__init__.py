from .FromHandler import FromHandler
from .JsonValue import JsonValue
from .TargetType import TargetType
from .ToHandler import ToHandler


_DESIGN_NOTES = """
# Serialize Annotations Sub-Package

Plain imports, no `__all__` (the package root decides what is public).

## Purpose
The named types that appear in the signatures of this library — and in yours,
when you write a handler or a wrapper around `serialize`.

## Internal Components Registry

| Component     | Type  | Description                                                                          |
| :------------ | :---- | :----------------------------------------------------------------------------------- |
| `ToHandler`   | Alias | `to_func(obj)` — turns an object into a value `serialize` understands.               |
| `FromHandler` | Alias | `from_func(data, annotation)` — builds an object back from data.                      |
| `JsonValue`   | Alias | What `serialize` returns: only `None`, `bool`, `int`, `float`, `str`, `list`, `dict`. |
| `TargetType`  | Alias | What `deserialize` accepts as its target: a class or a typing construct.              |

`Location` (the path to a value) is not here: nobody outside the library writes it, so
it is a private helper (`logic/_helpers`).
"""
