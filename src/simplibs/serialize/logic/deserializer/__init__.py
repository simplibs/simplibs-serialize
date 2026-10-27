from .deserialize import deserialize
from .is_deserializable import is_deserializable


_DESIGN_NOTES = """
# Deserializer Sub-Package

## Purpose
The way back: data and an annotation → a value of that annotation. It never imports the
way out (`serializer`); what both share is in `logic/_helpers` and `logic/_constants`.

## Internal Components Registry

| Component          | Type     | Description                                                              |
| :----------------- | :------- | :----------------------------------------------------------------------- |
| `deserialize`      | Function | Builds a value of the given annotation from ..d data.             |
| `is_deserializable`| Function | Dry run of `deserialize`: True if it would succeed, False otherwise.     |
| `_classes`         | Package  | `DeserializeContext` — what one `deserialize` call carries along.        |
| `_builders`        | Package  | One builder per kind of annotation, plus the dispatcher.                 |
| `_helpers`         | Package  | Alias detection, type hints, key candidates, union tie-breaker.          |
| `_validations`     | Package  | Diagnostic raisers for everything that can go wrong on the way back.     |

## What It Does Not Build
It builds what an annotation names. `serialize` accepts any `Mapping`, `Sequence` or
`Set` and writes it as a dict or a list, but the way back has no builder for
`defaultdict`, `Counter` or `ChainMap` (there is no way to know the default factory):
annotate such a field as `dict[...]` or `Mapping[...]`, or register a handler.
"""
