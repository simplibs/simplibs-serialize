from .find_from_handler import find_from_handler
from .find_to_handler import find_to_handler
from .register_type import register_type
from .unregister_type import unregister_type


_DESIGN_NOTES = """
# Serialize Registry Sub-Package

## Purpose
The table of types `serialize` and `deserialize` know by heart — datetimes,
paths, UUIDs, enums, ... — and the two public functions that let a caller add
a type of their own.

## Internal Components Registry

| Component           | Type     | Description                                                              |
| :------------------ | :------- | :----------------------------------------------------------------------- |
| `register_type`     | Function | Teaches the library a type: `to_func`, `from_func` or both.              |
| `unregister_type`   | Function | Removes a registration; a built-in handler it replaced comes back.       |
| `find_to_handler`   | Function | The handler `serialize` uses for the class of an object, or `None`.      |
| `find_from_handler` | Function | The handler `deserialize` uses for an annotation, or `None`.             |
| `_handlers`         | Package  | `builtin` — the fixed, read-only tables; `active` — the live copies plus every registration. |
| `_helpers`          | Package  | Lookup along the class hierarchy and the registration checks.            |
| `_validations`      | Package  | Diagnostic raisers for a wrong `register_type` call.                     |

## The Registry Is Global
One process, one table: a handler registered anywhere is used everywhere. That
is what a serializer wants (a type is registered once, at start-up), and it is
why `unregister_type` exists — a test can put the table back as it found it.
Changing the tables is not synchronized; register at start-up, not from threads
that run in parallel with `serialize`.
"""
