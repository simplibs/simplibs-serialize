import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_duplicate_key_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("key", ["1", "name"])
def test_raise_duplicate_key_error_contract(subtests, key, location, label) -> None:
    """Verify raise_duplicate_key_error produces a well-formed SerializationError card."""

    def raising_wrapper(target_location):
        raise_duplicate_key_error(target_location, key)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=SerializationError,
        error_name="SERIALIZE_DUPLICATE_KEY",
        label=label,
        value=key,
        problem=f"Two entries would be written under the key {key!r}; one would be lost.",
        expected="Keys that stay different after conversion to text.",
        how_to_fix=(
            "In a dict: do not mix keys such as 1 and '1' — they are the same text.",
            "In a dataclass: give the fields different aliases.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
