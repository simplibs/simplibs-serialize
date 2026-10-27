from .assert_round_trip import assert_round_trip

__all__ = [
    "assert_round_trip",
]


_DESIGN_NOTES = """
# simplibs.serialize.testing — Test Tools for Code That Uses the Library

## Purpose
One call that audits whether a value, a dataclass or a registered type survives
the trip out and back — for your own types and your own handlers.

## Internal Components Registry

| Component           | Type     | Description                                                      |
| :------------------ | :------- | :--------------------------------------------------------------- |
| `assert_round_trip` | Function | The value survives `serialize` → `deserialize` and `to_json` → `from_json`. |

## Domain Folder
Imported through its own folder (`from simplibs.serialize.testing import ...`),
not from the package root, like the testing tools of the other libraries.
"""
