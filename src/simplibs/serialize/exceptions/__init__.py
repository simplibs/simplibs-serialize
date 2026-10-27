from .SerializeError import SerializeError
from .SerializationError import SerializationError
from .DeserializationError import DeserializationError


_DESIGN_NOTES = """
# Serialize Exceptions Sub-Package

## Purpose
The three exception classes of `simplibs-serialize`: one root and one class per
direction, so a caller can catch the whole library or only one half of it.

## Internal Components Registry

| Component              | Type  | Description                                                     |
| :--------------------- | :---- | :-------------------------------------------------------------- |
| `SerializeError`       | Class | Root of every error raised by this library.                     |
| `SerializationError`   | Class | An object could not be turned into a JSON-compatible structure. |
| `DeserializationError` | Class | Data could not be turned back into the requested type.          |
"""
