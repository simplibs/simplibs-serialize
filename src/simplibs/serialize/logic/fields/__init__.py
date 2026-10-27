from .serialized_field import serialized_field


_DESIGN_NOTES = """
# Serialize Fields Sub-Package

## Purpose
How a dataclass field says what it is called in the data, or that it is not
data at all.

## Internal Components Registry

| Component          | Type     | Description                                                       |
| :----------------- | :------- | :---------------------------------------------------------------- |
| `serialized_field` | Function | `dataclasses.field` plus `alias` and `exclude`.                   |
"""
