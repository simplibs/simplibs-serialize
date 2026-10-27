from typing import Any, TypeVar, overload
from simplibs.file import EncodingErrors, EncodingName, read_json
from simplibs.path import PathLike
from simplibs.validate import validate_call
# Outers
from ...annotations import TargetType
from ..deserializer import deserialize
# Annotations
T = TypeVar("T")


@overload
def load_json_file(
    path: PathLike,
    annotation: type[T],
    *,
    strict: bool = True,
    encoding: EncodingName = "utf-8-sig",
    errors: EncodingErrors = "strict",
) -> T: ...
@overload
def load_json_file(
    path: PathLike,
    annotation: TargetType,
    *,
    strict: bool = True,
    encoding: EncodingName = "utf-8-sig",
    errors: EncodingErrors = "strict",
) -> Any: ...


@validate_call
def load_json_file(
    path: PathLike,
    annotation: TargetType,
    *,
    strict: bool = True,
    encoding: EncodingName = "utf-8-sig",
    errors: EncodingErrors = "strict",
) -> Any:
    """Read a JSON file and build a value of the given type from it.

    Args:
        path: The JSON file.
        annotation: What to build: a class, `list[Point]`, `dict[str, int]`, ...
        strict: As for `deserialize`: unknown keys are an error.
        encoding: The text encoding. The default tolerates a BOM.
        errors: How to treat bytes the encoding cannot decode.

    Returns:
        A value of the requested type.

    Raises:
        DeserializationError: If the JSON does not fit the annotation.
        ConversionError: If the file is not valid text or valid JSON (from `read_json`).
        NotFoundError, StateError, AccessError: As for `read_json`.
    """

    # 1. Reading and parsing — BOM, encoding, syntax errors with a position — is `read_json`
    data = read_json(path, encoding=encoding, errors=errors)

    # 2. Build the value
    return deserialize(data, annotation, strict=strict)


_DESIGN_NOTES = """
# load_json_file — JSON File to Object
## Path First
As `read_json(path)`, `read_text(path)` and `dump_json_file(path, obj)`.

## Two Kinds of Failure
A file that is not JSON fails in `read_json` (a `ConversionError` from
`simplibs-file`); JSON that does not fit the type fails in `deserialize` (a
`DeserializationError` with the location of the bad value). Both are a
`ConversionError`.
"""
