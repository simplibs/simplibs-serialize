import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._validations import raise_key_collision_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize(
    "key, first, second",
    [(1.0, "1.0", "1.00"), (1, "1", "true")],
    ids=["float_spellings", "int_and_bool"],
)
def test_raise_key_collision_error_contract(subtests, key, first, second, location, label) -> None:
    """Verify raise_key_collision_error produces a well-formed DeserializationError card."""

    def raising_wrapper(target_location):
        raise_key_collision_error(target_location, key, first, second)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_KEY_COLLISION",
        label=label,
        value=second,
        problem=f"The keys {first!r} and {second!r} both stand for {key!r}; one value would be lost.",
        expected="Keys that stay different after they are read back.",
        how_to_fix=(
            "Remove one of the two entries from the data.",
            "Or annotate the keys as `str`, which keeps the text as it is.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
