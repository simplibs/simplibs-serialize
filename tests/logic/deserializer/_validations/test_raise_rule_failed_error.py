import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._validations import raise_rule_failed_error


class _DescribedRule:
    """A rule that can say in its own words what it requires."""

    def describe(self) -> str:
        return "greater than 0"


class _BrokenRule:
    """A rule whose describe() fails, so the card has to fall back on repr()."""

    def describe(self) -> str:
        raise RuntimeError("cannot describe")

    def __repr__(self) -> str:
        return "<broken rule>"


def _is_positive(value) -> bool:
    """A plain predicate, which has a name but no describe()."""
    return value > 0


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_RULES = [
    pytest.param(_DescribedRule(), "greater than 0", id="describe"),
    pytest.param(_is_positive, "_is_positive", id="function_name"),
    pytest.param(_BrokenRule(), "<broken rule>", id="repr_fallback"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("rule, required", _RULES)
def test_raise_rule_failed_error_contract(subtests, rule, required, location, label) -> None:
    """Verify raise_rule_failed_error produces a well-formed DeserializationError card."""
    value = -5

    def raising_wrapper(target_location):
        raise_rule_failed_error(target_location, rule, value)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_RULE_FAILED",
        label=label,
        value=value,
        problem=f"The value {value!r} does not satisfy the rule: {required}.",
        expected=required,
        how_to_fix="Correct the data so that it satisfies the rule of the type.",
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
