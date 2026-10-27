from typing import Final


FIELD_EXCLUDE_OPTION: Final[str] = "exclude"
"""The field option that keeps the field out of the data."""


_DESIGN_NOTES = """
# FIELD_EXCLUDE_OPTION — A Field That Is Not Data

## Purpose
Caches, handles and secrets belong on the object but not in the file. An
excluded field is skipped by `serialize`, and `deserialize` leaves it to its
default.
"""
