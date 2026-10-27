from .is_serializable import is_serializable
from .serialize import serialize


_DESIGN_NOTES = """
# Serializer Sub-Package

## Purpose
The way out: Python object → structure of `None`, `bool`, `int`, `float`, `str`, `list`
and `dict`. It never imports the way back (`deserializer`); what both share is in
`logic/_helpers` and `logic/_constants`.

## Internal Components Registry

| Component         | Type     | Description                                                          |
| :---------------- | :------- | :------------------------------------------------------------------- |
| `serialize`       | Function | Turns any supported object into a JSON-compatible structure.         |
| `is_serializable` | Function | Dry run of `serialize`: True if it would succeed, False otherwise.   |
| `_classes`        | Package  | `SerializeContext` — what one `serialize` call carries along.        |
| `_encoders`       | Package  | One encoder per kind of value, plus the dispatcher.                  |
| `_helpers`        | Package  | Set ordering and primitive conversion.                               |
| `_validations`    | Package  | Diagnostic raisers for everything that can go wrong on the way out.  |
"""
