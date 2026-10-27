from typing import Final


FIELD_ALIAS_OPTION: Final[str] = "alias"
"""The field option holding the name the field has in the data."""


_DESIGN_NOTES = """
# FIELD_ALIAS_OPTION — A Different Name in the Data

## Purpose
Foreign formats do not follow Python naming (`userName`, `user-name`). The alias
is the name written by `serialize` and expected by `deserialize`, while the
attribute keeps its Python name.
"""
