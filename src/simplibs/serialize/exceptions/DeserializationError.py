# Inners
from .SerializeError import SerializeError


class DeserializationError(SerializeError):
    """Raised when serialized data cannot be reconstructed into the target type."""


_DESIGN_NOTES = """
# DeserializationError — The Way Back Failed

## Purpose
Raised by `deserialize`, `from_json` and `load_json_file` when the data does not
fit the requested type: a wrong shape, a missing field, an invalid enum value,
an ambiguous union.
"""
