import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_unsupported_key_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_KEYS = [
    pytest.param((1, 2), "tuple", id="tuple"),
    pytest.param(frozenset({1}), "frozenset", id="frozenset"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("key, type_name", _KEYS)
def test_raise_unsupported_key_error_contract(subtests, key, type_name, location, label) -> None:
    """Verify raise_unsupported_key_error produces a well-formed SerializationError card."""

    def raising_wrapper(target_location):
        raise_unsupported_key_error(target_location, key)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=SerializationError,
        error_name="SERIALIZE_UNSUPPORTED_KEY",
        label=label,
        value=key,
        problem=f"The key {key!r} ('{type_name}') has no text form.",
        expected="A key that is text, a number, a bool, None, or converts to text (enum, date, UUID, ...).",
        how_to_fix=(
            "Use text keys, for example '1,2' instead of the tuple (1, 2).",
            "Or turn the mapping into a list of {'key': ..., 'value': ...} entries before serializing.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
