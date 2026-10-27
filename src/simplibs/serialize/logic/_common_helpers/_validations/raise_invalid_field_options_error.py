from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_invalid_field_options_error(
    field_name: str,
    options: Any,
    problem: str
) -> NoReturn:
    """Raise ParamError when a dataclass field has broken serialize options.

    Args:
        field_name: The name of the field in the class.
        options: What was found under the serialize key of the field's metadata.
        problem: What exactly is wrong with it.
    """

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="SERIALIZE_INVALID_FIELD_OPTIONS",
        label=f"field '{field_name}' metadata",
        value=options,
        problem=problem,
        expected="A mapping with `alias` (non-empty text) and/or `exclude` (bool).",
        how_to_fix=(
            "Declare the field with serialized_field(alias=..., exclude=...).",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_invalid_field_options_error — A Field Declared Wrong

## Purpose
The mistake is in the class, not in the data, so it is a `ParamError` and it
is raised even by `is_serializable` — that function answers "is this data
fine", not "is my class declared correctly".
"""
