from .DeserializeContext import DeserializeContext


_DESIGN_NOTES = """
# Deserializer Classes Sub-Package

## Purpose
The one small class the builders share.

## Internal Components Registry

| Component            | Type  | Description                                                |
| :------------------- | :---- | :--------------------------------------------------------- |
| `DeserializeContext` | Class | The settings of one `deserialize` call and its dispatcher. |
"""
