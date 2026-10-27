import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_wrong_type_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(int, "5", "text", id="text_for_int"),
    pytest.param(list[int], {"a": 1}, "an object", id="object_for_list"),
    pytest.param(str, None, "null", id="null_for_str"),
    pytest.param(int, [1, 2], "a list", id="list_for_int"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation, data, kind", _CASES)
def test_raise_wrong_type_error_contract(subtests, annotation, data, kind, location, label) -> None:
    """Verify raise_wrong_type_error produces a well-formed DeserializationError card."""
    wanted = describe_annotation(annotation)

    def raising_wrapper(target_location):
        raise_wrong_type_error(target_location, annotation, data)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_WRONG_TYPE",
        label=label,
        value=data,
        problem=f"Got {kind}, but the data should be {wanted}.",
        expected=wanted,
        how_to_fix="Correct the data at this location so that it has the shape the type needs.",
        exception=TypeError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
