from typing import NoReturn
# Outers
from ....exceptions import SerializationError
from ..._common_helpers import format_location, Location


def raise_non_finite_number_error(
    location: Location,
    value: float
) -> NoReturn:
    """Raise SerializationError for a `nan` or `inf` when they are not allowed.

    Args:
        location: Where in the data the number sits.
        value: The number.
    """

    # 1. Raise structured SerializationError wrapping a ValueError
    raise SerializationError(
        error_name="SERIALIZE_NON_FINITE_NUMBER",
        label=format_location(location),
        value=value,
        problem=f"{value!r} is not a valid JSON number.",
        expected="A finite number.",
        how_to_fix=(
            "Replace it with None, or with a value that means 'missing' for your data.",
            "Pass allow_nan=True if the reader accepts NaN and Infinity (most do not).",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_non_finite_number_error — Not a Number in JSON

## Purpose
`json.dumps` happily writes `NaN`, and most parsers then refuse the file. The
error belongs where the number is made, not in whatever program reads it.
"""
