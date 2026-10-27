from .FromJson import FromJson
from .ToJson import ToJson


_DESIGN_NOTES = """
# Serialize Actions Text Sub-Package

## Purpose
JSON as a string: for messages, API bodies, logs, and everything that is not a file.

## Internal Components Registry

| Component  | Type   | Description                                               |
| :--------- | :----- | :-------------------------------------------------------- |
| `ToJson`   | Action | Object → JSON text.                                       |
| `FromJson` | Action | JSON text → an object of the configured annotation.       |
"""
