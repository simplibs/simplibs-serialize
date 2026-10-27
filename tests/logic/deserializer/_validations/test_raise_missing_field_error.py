from dataclasses import dataclass

import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_missing_field_error


@dataclass
class User:
    name: str
    age: int


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(["name"], "'name'", id="one_name"),
    pytest.param(["name", "age"], "'name', 'age'", id="several_names"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("names, listed", _CASES)
def test_raise_missing_field_error_contract(subtests, names, listed, location, label) -> None:
    """Verify raise_missing_field_error produces a well-formed DeserializationError card."""

    def raising_wrapper(target_location):
        raise_missing_field_error(target_location, User, names)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_MISSING_FIELD",
        label=label,
        value=names,
        problem=f"{describe_annotation(User)} is missing the required: {listed}.",
        expected=f"Every field without a default: {listed}.",
        how_to_fix=(
            "Add the missing keys to the data.",
            "Or give the field a default in the class.",
            "A field excluded with serialized_field(exclude=True) needs a default too.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
