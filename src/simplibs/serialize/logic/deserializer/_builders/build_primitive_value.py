from typing import Any
# Outers
from ..._constants import JSON_PRIMITIVES
from ..._common_helpers import Location
from .._validations import raise_build_failed_error, raise_wrong_type_error


def build_primitive_value(data: Any, annotation: type, location: Location) -> Any:
    """Check that data is the primitive the annotation asks for, and return it.

    Args:
        data: The serialized data at this location.
        annotation: `str`, `int`, `float`, `bool`, or a subclass of one of them.
        location: Where in the data this value sits.

    Returns:
        The value; for a subclass (`class Port(int)`), an instance of it.
    """

    # 1. The primitive the annotation stands on
    base = annotation if annotation in JSON_PRIMITIVES else next(
        candidate for candidate in JSON_PRIMITIVES if issubclass(annotation, candidate)
    )

    # 2. The data must be that primitive — a bool is not an int, a float is not an int
    if base is bool:
        valid = isinstance(data, bool)
    elif base is int:
        valid = isinstance(data, int) and not isinstance(data, bool)
    elif base is float:
        valid = isinstance(data, (int, float)) and not isinstance(data, bool)
    else:
        valid = isinstance(data, str)
    if not valid:
        raise_wrong_type_error(location, annotation, data)

    # 3. An int may stand for a float, and only that conversion is made
    value = data
    if base is float:
        try:
            value = float(data)
        except OverflowError as caught:
            raise_build_failed_error(location, annotation, caught)

    # 4. The plain value, or the subclass built from it
    if annotation is base:
        return value
    try:
        return annotation(value)
    except RecursionError:
        raise
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)


_DESIGN_NOTES = """
# build_primitive_value — Checked, Not Passed Through

## Purpose
Returning the data untouched whenever the annotation is a primitive would make
`deserialize("abc", int)` return `"abc"`, and a typo in a config file would travel
on into the program.

## What Counts as a Fit
* `str`: text. `bool`: a bool. `int`: an int that is not a bool.
* `float`: a float or an int (`1` is a fine `1.0`); never a bool.
* Not accepted for `int`: `1.0`, `"1"`, `True`. Silent casts hide mistakes.

## Subclasses
`class Port(int)` is built as `Port(value)`; a constructor that refuses the
value is a card, not a bare exception.

## Recursion Limit
A `RecursionError` is let through unhandled so that excessive nesting always results 
in a clean `DATA_TOO_DEEP` card at the root, regardless of where the limit was hit.
"""
