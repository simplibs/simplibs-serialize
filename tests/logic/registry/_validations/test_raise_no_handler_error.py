from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize.logic.registry._validations import raise_no_handler_error


def test_raise_no_handler_error_contract(subtests) -> None:
    """Verify raise_no_handler_error produces a well-formed ParamError card."""
    exc = assert_exception_function(
        subtests,
        raise_no_handler_error,
        invalid_params=(),
        exception_type=ParamError,
        error_name="SERIALIZE_REGISTER_NO_HANDLER",
        label="to_func / from_func",
        problem="register_type() was called without any handler.",
        expected="At least one of `to_func` and `from_func`.",
        how_to_fix=(
            "Pass `to_func` to teach `serialize` this type.",
            "Pass `from_func` to teach `deserialize` this type.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
