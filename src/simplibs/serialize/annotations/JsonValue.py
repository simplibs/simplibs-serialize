from typing import TypeAlias


JsonValue: TypeAlias = "None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]"
"""Everything `serialize` can return — exactly what `json.dumps` accepts."""


_DESIGN_NOTES = """
# JsonValue — What Comes Out of `serialize`

## Purpose
A readable return type for functions that hand the result of `serialize` on.

## For Hints Only
The alias refers to itself, so it is written as a string. A type checker and a
reader understand it; a runtime check (`validate_call`) would only see the
string. Use it in return annotations, not as a validated parameter type.
"""
