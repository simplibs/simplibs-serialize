# Outers
from .._constants import LOCATION_ROOT
# Inners
from .Location import Location


def format_location(
    location: Location
) -> str:
    """Write a location as text: `("items", 2, "name")` → `$.items[2].name`.

    Args:
        location: The keys and indexes from the root to a value.

    Returns:
        The location as JSONPath-like text; the root alone is `$`.
    """

    # 1. Start at the root
    parts = [LOCATION_ROOT]

    # 2. An index in brackets, a plain name after a dot, anything else quoted
    for segment in location:
        if isinstance(segment, int):
            parts.append(f"[{segment}]")
        elif segment.isidentifier():
            parts.append(f".{segment}")
        else:
            parts.append(f"[{segment!r}]")

    # 3. One text
    return "".join(parts)


_DESIGN_NOTES = """
# format_location — Where, in One Line

## Purpose
`$.servers[2].host` says in one glance what "the third server's host" says in a
sentence — and a reader of JSON already knows the notation.

## Quoted When Needed
A key with a space, a dot or a dash (`"user-name"`, `"a.b"`) would be ambiguous
after a dot, so it is written as `['user-name']`.
"""
