import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize.logic.registry._validations import raise_not_registrable_type_error


@pytest.mark.parametrize("type_", ["Point", 42, 3.5], ids=["text", "integer", "float"])
def test_raise_not_registrable_type_error_contract(subtests, type_) -> None:
    """Verify raise_not_registrable_type_error produces a well-formed ParamError card."""

    def raising_wrapper(target):
        raise_not_registrable_type_error(target)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(type_,),
        exception_type=ParamError,
        error_name="SERIALIZE_REGISTER_NOT_A_TYPE",
        label="type_",
        value=type_,
        problem=f"{type_!r} is not a type, so no data could ever be matched to it.",
        expected="A class, a subscripted annotation such as `list[int]`, or a `NewType`.",
        how_to_fix="Pass the class itself (`Point`), not an instance or its name as a string.",
        exception=TypeError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
