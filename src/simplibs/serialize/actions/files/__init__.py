from .DumpJsonFile import DumpJsonFile
from .LoadJsonFile import LoadJsonFile


_DESIGN_NOTES = """
# Serialize Actions Files Sub-Package

## Purpose
JSON on disk, content-focused: the OBJECT flows through the pipeline, the path
is configuration — except for loading, where the path is the thing that flows.

## Internal Components Registry

| Component      | Type   | Description                                                   |
| :------------- | :----- | :------------------------------------------------------------ |
| `DumpJsonFile` | Action | Writes the object flowing in to the configured path.          |
| `LoadJsonFile` | Action | Reads the file flowing in as the configured annotation.       |
"""
