from typing import Final


LOCATION_ROOT: Final[str] = "$"
"""The symbol every rendered location starts with (`$.items[2].name`)."""


_DESIGN_NOTES = """
# LOCATION_ROOT — The Start of Every Location

## Purpose
The `$` is the JSONPath convention for "the whole document", so the location in
a card reads the same way a developer already knows it.
"""
