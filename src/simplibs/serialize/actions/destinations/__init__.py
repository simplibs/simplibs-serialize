from .DumpJsonFileTo import DumpJsonFileTo


_DESIGN_NOTES = """
# Serialize Actions Destinations Sub-Package

## Purpose
Pipeline actions wrapping `dump_json_file` where the **path** is the main
pipeline input and the object is configured as a parameter — the counterpart of
the content-focused `files` sub-package.

## Internal Components Registry

| Component        | Type   | Description                                                 |
| :--------------- | :----- | :---------------------------------------------------------- |
| `DumpJsonFileTo` | Action | Writes the configured `obj` to the path flowing in.         |
"""
