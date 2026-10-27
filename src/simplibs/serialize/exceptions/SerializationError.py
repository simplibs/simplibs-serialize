# Inners
from .SerializeError import SerializeError


class SerializationError(SerializeError):
    """Raised when an object cannot be converted into a JSON-compatible structure."""


_DESIGN_NOTES = """
# SerializationError — The Way Out Failed

## Purpose
Raised by `serialize`, `to_json` and `dump_json_file` for a value that cannot be
written: an unsupported type, a circular reference, a `NaN`.
"""
