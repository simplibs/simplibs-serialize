from .find_handler import find_handler
from .is_plain_class import is_plain_class
from .is_registrable_type import is_registrable_type
from .reset_handler import reset_handler


_DESIGN_NOTES = """
# Registry Helpers Sub-Package

## Purpose
Private helpers of the registry: how a handler is found and what may be
registered.

## Internal Components Registry

| Component             | Type     | Description                                                        |
| :-------------------- | :------- | :----------------------------------------------------------------- |
| `find_handler`        | Function | Exact match first, then the nearest base class.                    |
| `is_plain_class`      | Function | True for a real class, False for `list[int]` and the like.         |
| `is_registrable_type` | Function | True for a class, a subscripted annotation or a `NewType`.         |
| `reset_handler`       | Function | Puts one table entry back to the built-in handler or removes it.   |
"""
