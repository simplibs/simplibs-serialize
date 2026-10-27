from .SerializeContext import SerializeContext


_DESIGN_NOTES = """
# Serialize Classes Sub-Package

## Purpose
The one small class the encoders share.

## Internal Components Registry

| Component          | Type  | Description                                              |
| :----------------- | :---- | :------------------------------------------------------- |
| `SerializeContext` | Class | The settings and the bookkeeping of one `serialize` call. |
"""
