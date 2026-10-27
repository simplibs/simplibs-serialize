from typing import Final


FIELD_METADATA_KEY: Final[str] = "simplibs.serialize"
"""The `metadata` key under which a dataclass field carries its serialize options."""


_DESIGN_NOTES = """
# FIELD_METADATA_KEY — Where a Field Keeps Its Options

## Purpose
`dataclasses.field(metadata=...)` is the standard place for per-field extras, so
a field can be renamed or left out without a second configuration object.
The value under this key is a dict with the options named by
`FIELD_ALIAS_OPTION` and `FIELD_EXCLUDE_OPTION`.

## Namespaced
The dotted name keeps the key from colliding with the metadata other tools put
on the same field.
"""
