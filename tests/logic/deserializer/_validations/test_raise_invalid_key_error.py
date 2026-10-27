import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_invalid_key_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation, key", [(int, "abc"), (float, "1,5")], ids=["int", "float"])
def test_raise_invalid_key_error_contract(subtests, annotation, key, location, label) -> None:
    """Verify raise_invalid_key_error produces a well-formed DeserializationError card."""
    wanted = describe_annotation(annotation)

    def raising_wrapper(target_location):
        raise_invalid_key_error(target_location, annotation, key)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_INVALID_KEY",
        label=label,
        value=key,
        problem=f"The key {key!r} cannot be read as {wanted}.",
        expected=f"A key that is a valid {wanted}, written as text.",
        how_to_fix="Correct the key in the data, or change the key type of the annotation.",
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
