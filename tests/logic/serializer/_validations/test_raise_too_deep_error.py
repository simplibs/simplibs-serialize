from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_too_deep_error


def test_raise_too_deep_error_contract(subtests) -> None:
    """Verify raise_too_deep_error produces a well-formed SerializationError card."""
    exc = assert_exception_function(
        subtests,
        raise_too_deep_error,
        invalid_params=(),
        exception_type=SerializationError,
        error_name="SERIALIZE_TOO_DEEP",
        label="obj",
        problem="The structure is nested too deep to convert.",
        expected="A structure of reasonable depth, without loops.",
        how_to_fix=(
            "Check for a handler that keeps returning a value of its own type.",
            "Check for an object that reaches itself only through a handler.",
            "Flatten extremely deep data before serializing it.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
