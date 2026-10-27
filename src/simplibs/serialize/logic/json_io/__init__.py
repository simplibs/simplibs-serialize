from .dump_json_file import dump_json_file
from .from_json import from_json
from .load_json_file import load_json_file
from .to_json import to_json


_DESIGN_NOTES = """
# Serialize JSON I/O Sub-Package

## Purpose
`serialize` and `deserialize` work with structures; these four functions add the
last step — JSON text, and a JSON file.

## Internal Components Registry

| Component        | Type     | Description                                                      |
| :--------------- | :------- | :--------------------------------------------------------------- |
| `to_json`        | Function | Python object → JSON text.                                       |
| `from_json`      | Function | JSON text + annotation → Python object.                          |
| `dump_json_file` | Function | Python object → JSON file (atomic, through `simplibs-file`).     |
| `load_json_file` | Function | JSON file + annotation → Python object.                          |
| `_validations`   | Package  | The card for text that is not valid JSON.                        |

## Files Belong to `simplibs-file`
Reading, writing, the BOM, the atomic swap, encodings and every file-system
error are `simplibs-file`'s job and its cards. This package only puts
`serialize` in front of `write_json` and `deserialize` behind `read_json`; it does
not touch a path or a byte itself.

## Which Error Is Which
* The value cannot be written: `SerializationError`.
* The text is not JSON (`from_json`): `DeserializationError`.
* The file contains invalid JSON (`load_json_file`): `ConversionError` from
  `read_json`, with line and column. `SerializeError` is itself a
  `ConversionError`, so `except ConversionError` covers the whole file round trip.
* The JSON is fine but does not fit the type: `DeserializationError`.
* The file is missing, locked, a directory...: `simplibs-file`'s own errors.
"""
