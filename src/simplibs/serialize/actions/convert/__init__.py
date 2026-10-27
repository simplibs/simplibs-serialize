from .Deserialize import Deserialize
from .Serialize import Serialize


_DESIGN_NOTES = """
# Serialize Actions Convert Sub-Package

## Purpose
The two directions between Python objects and JSON-compatible structures.

## Internal Components Registry

| Component     | Type   | Description                                                  |
| :------------ | :----- | :----------------------------------------------------------- |
| `Serialize`   | Action | Object → structure of `None`, `bool`, `int`, `float`, `str`, `list`, `dict`. |
| `Deserialize` | Action | Structure → an object of the configured annotation.          |
"""
