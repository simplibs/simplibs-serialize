import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize.rules._validations import raise_rule_param_invalid_error


_CASES = [
    pytest.param("IsSerializable", "allow_nan", "yes", "a bool", {}, ValueError, id="default_exception"),
    pytest.param("IsDeserializable", "strict", 5, "a bool", {"exception": TypeError}, TypeError, id="type_error"),
]


@pytest.mark.parametrize("rule_name, param_name, value, expected, extra, wrapped", _CASES)
def test_raise_rule_param_invalid_error_contract(
    subtests, rule_name, param_name, value, expected, extra, wrapped
) -> None:
    """Verify raise_rule_param_invalid_error produces a well-formed ParamError card."""

    def raising_wrapper(target_rule):
        raise_rule_param_invalid_error(target_rule, param_name, value, expected, **extra)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(rule_name,),
        exception_type=ParamError,
        error_name="RULE_PARAM_INVALID",
        label=f"{rule_name} parameter '{param_name}'",
        value=value,
        problem=f"Invalid value {value!r} for parameter '{param_name}' of {rule_name}.",
        expected=expected,
        how_to_fix=f"Pass {expected} as '{param_name}'.",
        exception=wrapped,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, wrapped)
