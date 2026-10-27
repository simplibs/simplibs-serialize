import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize.logic._common_helpers._validations import raise_invalid_field_options_error


_CASES = [
    pytest.param("name", {"alias": ""}, "The alias must be non-empty text.", id="empty_alias"),
    pytest.param("age", "yes", "The serialize options must be a mapping.", id="not_a_mapping"),
]


@pytest.mark.parametrize("field_name, options, problem", _CASES)
def test_raise_invalid_field_options_error_contract(subtests, field_name, options, problem) -> None:
    """Verify raise_invalid_field_options_error produces a well-formed ParamError card."""

    def raising_wrapper(target_name):
        raise_invalid_field_options_error(target_name, options, problem)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(field_name,),
        exception_type=ParamError,
        error_name="SERIALIZE_INVALID_FIELD_OPTIONS",
        label=f"field '{field_name}' metadata",
        value=options,
        problem=problem,
        expected="A mapping with `alias` (non-empty text) and/or `exclude` (bool).",
        how_to_fix="Declare the field with serialized_field(alias=..., exclude=...).",
        exception=ValueError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
