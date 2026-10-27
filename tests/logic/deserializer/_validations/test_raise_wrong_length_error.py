import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_wrong_length_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(tuple[int, int], [1, 2, 3], 2, 2, "2 items", id="exact_length"),
    pytest.param(tuple[int, int, int], [], 1, 3, "1 to 3 items", id="range_of_lengths"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation, data, minimum, maximum, wanted", _CASES)
def test_raise_wrong_length_error_contract(
    subtests, annotation, data, minimum, maximum, wanted, location, label
) -> None:
    """Verify raise_wrong_length_error produces a well-formed DeserializationError card."""

    def raising_wrapper(target_location):
        raise_wrong_length_error(target_location, annotation, data, minimum, maximum)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_WRONG_LENGTH",
        label=label,
        value=data,
        problem=f"Got {len(data)} items, but {describe_annotation(annotation)} needs {wanted}.",
        expected=wanted,
        how_to_fix="Add or remove items so that the list has the length the type needs.",
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
