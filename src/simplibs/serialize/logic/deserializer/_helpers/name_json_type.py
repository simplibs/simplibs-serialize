from collections.abc import Mapping
from typing import Any


def name_json_type(
    data: Any
) -> str:
    """Name the JSON kind of a value in a few words.

    Args:
        data: Anything that can be in decoded JSON.

    Returns:
        `null`, `a boolean`, `an integer`, `a number`, `text`, `a list`, `an object`;
        for anything else, its class name.
    """

    # 1. JSON kinds, `bool` before `int` because it is one
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "a boolean"
    if isinstance(data, int):
        return "an integer"
    if isinstance(data, float):
        return "a number"
    if isinstance(data, str):
        return "text"
    if isinstance(data, (list, tuple)):
        return "a list"
    if isinstance(data, Mapping):
        return "an object"

    # 2. Not JSON at all
    return f"a {type(data).__name__}"


_DESIGN_NOTES = """
# name_json_type — What the Data Is

## Purpose
"Got `text`, expected `int`" is what a person reading a JSON file thinks in; "got
`str`" is what Python says. The card speaks JSON.
"""
