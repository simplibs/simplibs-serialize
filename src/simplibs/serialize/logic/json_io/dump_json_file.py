from pathlib import Path
from typing import Any
from simplibs.file import EncodingName, NewlineMode, write_json
from simplibs.path import PathLike
from simplibs.validate import validate_call
# Outers
from ...annotations import ToHandler
from ..serializer import serialize


@validate_call
def dump_json_file(
    path: PathLike,
    obj: Any,
    *,
    indent: int | str | None = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    allow_nan: bool = False,
    default: ToHandler | None = None,
    trailing_newline: bool = True,
    encoding: EncodingName = "utf-8",
    newline: NewlineMode = "\n",
    overwrite: bool = True,
    use_draft: bool = True,
    sync: bool = False,
) -> Path:
    """Write an object to a JSON file.

    The object is converted in memory first, so a value that cannot be written
    fails before the disk is touched. The file itself is written by
    `simplibs.file.write_json` — atomically, by default.

    Args:
        path: The target file. Its folder is created if missing.
        obj: The object to write.
        indent: Indentation: a number of spaces, a string, or None for compact output.
        ensure_ascii: If False (default), non-ASCII text is written as it is.
        sort_keys: If True, object keys are sorted — clean diffs.
        allow_nan: If False (default), `NaN` and `Infinity` are an error.
        default: The fallback for an object nothing else can convert; see `serialize`.
        trailing_newline: If True (default), the file ends with a line ending.
        encoding: The text encoding of the file.
        newline: The line ending written for every `"\\n"`.
        overwrite: If False, an existing file is an error instead of being replaced.
        use_draft: Draft-and-swap write (default) or an in-place write.
        sync: Force the data to stable storage before the swap.

    Returns:
        The normalized target `Path`.

    Raises:
        SerializationError: If the object cannot be converted.
        AlreadyExistsError, StateError, AccessError: As for `write_json`.
    """

    # 1. Convert first — an unsupported value never reaches the file system
    structure = serialize(obj, default=default, allow_nan=allow_nan)

    # 2. Everything about the file is `write_json`'s business
    return write_json(
        path,
        structure,
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        allow_nan=allow_nan,
        trailing_newline=trailing_newline,
        encoding=encoding,
        newline=newline,
        overwrite=overwrite,
        use_draft=use_draft,
        sync=sync,
    )


_DESIGN_NOTES = """
# dump_json_file — Object to JSON File
## Path First
`write_json(path, data)` and `write_text(path, text)` take the path first, so this
does too; the draft had the object first like `json.dump(obj, fp)`. One order
across the ecosystem is easier to remember than agreement with the standard
library's file-handle function.

## Two Steps on Purpose
`write_json` could be given the original object with a `default`, but then the
type conversion would be done by `json.dumps` and the library's own rules —
dataclasses, enums, registered types, locations in errors — would not run.
"""
