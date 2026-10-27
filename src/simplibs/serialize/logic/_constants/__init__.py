from .FIELD_ALIAS_OPTION import FIELD_ALIAS_OPTION
from .FIELD_EXCLUDE_OPTION import FIELD_EXCLUDE_OPTION
from .FIELD_METADATA_KEY import FIELD_METADATA_KEY
from .JSON_PRIMITIVES import JSON_PRIMITIVES
from .LOCATION_ROOT import LOCATION_ROOT


_DESIGN_NOTES = """
# Serialize Constants Sub-Package

Plain imports, no `__all__` (the package root decides what is public).

## Purpose
The fixed words and groups both directions of the library agree on. Private: nothing
here is part of the public API, so it lives next to `_helpers`, not in `commons`.

## Internal Components Registry

| Component              | Type     | Description                                                                |
| :--------------------- | :------- | :------------------------------------------------------------------------- |
| `JSON_PRIMITIVES`      | Constant | The exact types JSON writes as they are: `str`, `int`, `float`, `bool`.    |
| `LOCATION_ROOT`        | Constant | The text a location starts with (`$`).                                     |
| `FIELD_METADATA_KEY`   | Constant | The key under which `serialized_field` stores its options in `metadata`.   |
| `FIELD_ALIAS_OPTION`   | Constant | The name of the alias option inside those options.                         |
| `FIELD_EXCLUDE_OPTION` | Constant | The name of the exclusion option inside those options.                     |
"""
