from dataclasses import dataclass

import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_unknown_field_error


@dataclass
class User:
    username: str


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(
        ["usernmae"], ["username"], "'usernmae'",
        " Required but absent: 'username' — a misspelled name?",
        id="misspelled_name",
    ),
    pytest.param(["a", "b"], [], "'a', 'b'", "", id="no_hint"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("unknown, missing, listed, hint", _CASES)
def test_raise_unknown_field_error_contract(
    subtests, unknown, missing, listed, hint, location, label
) -> None:
    """Verify raise_unknown_field_error produces a well-formed DeserializationError card."""

    def raising_wrapper(target_location):
        raise_unknown_field_error(target_location, User, unknown, missing)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_UNKNOWN_FIELD",
        label=label,
        value=unknown,
        problem=f"{describe_annotation(User)} has no such key: {listed}.{hint}",
        expected="Only the keys the class defines (under their alias, if it has one).",
        how_to_fix=(
            "Remove or rename the unknown keys.",
            "Or pass strict=False to deserialize() to ignore them.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The tool only checks that the text is included, so the missing hint needs its own check
    assert ("Required but absent" in str(exc.problem)) is bool(missing)

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
