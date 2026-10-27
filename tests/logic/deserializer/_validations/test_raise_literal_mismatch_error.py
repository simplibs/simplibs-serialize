from typing import Literal

import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._validations import raise_literal_mismatch_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(Literal["red", "green"], "blue", "'red', 'green'", id="text"),
    pytest.param(Literal[1, 2], 3, "1, 2", id="numbers"),
    pytest.param(Literal[1], True, "1", id="bool_is_not_int"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation, data, allowed", _CASES)
def test_raise_literal_mismatch_error_contract(subtests, annotation, data, allowed, location, label) -> None:
    """Verify raise_literal_mismatch_error produces a well-formed DeserializationError card."""

    def raising_wrapper(target_location):
        raise_literal_mismatch_error(target_location, annotation, data)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_LITERAL_MISMATCH",
        label=label,
        value=data,
        problem=f"{data!r} is not one of the allowed values.",
        expected=f"One of: {allowed}.",
        how_to_fix="Use one of the listed values — the type of the value matters (`1` is not `True`).",
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
