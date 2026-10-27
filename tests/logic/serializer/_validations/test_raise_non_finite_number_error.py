import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_non_finite_number_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize(
    "number",
    [float("nan"), float("inf"), float("-inf")],
    ids=["nan", "inf", "minus_inf"],
)
def test_raise_non_finite_number_error_contract(subtests, number, location, label) -> None:
    """Verify raise_non_finite_number_error produces a well-formed SerializationError card."""

    def raising_wrapper(target_location):
        raise_non_finite_number_error(target_location, number)

    # `value` is left out of the call: the tool compares it with ==, and nan is not equal to itself
    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=SerializationError,
        error_name="SERIALIZE_NON_FINITE_NUMBER",
        label=label,
        problem=f"{number!r} is not a valid JSON number.",
        expected="A finite number.",
        how_to_fix=(
            "Replace it with None, or with a value that means 'missing' for your data.",
            "Pass allow_nan=True if the reader accepts NaN and Infinity (most do not).",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The number is compared through its text, which works for nan as well
    assert repr(exc.value) == repr(number)

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
