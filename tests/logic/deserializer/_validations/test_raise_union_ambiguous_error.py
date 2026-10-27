import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_union_ambiguous_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(list[int] | list[str], [], [list[int], list[str]], id="lists"),
    pytest.param(int | str, "1", [int, str], id="scalars"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation, data, matched", _CASES)
def test_raise_union_ambiguous_error_contract(subtests, annotation, data, matched, location, label) -> None:
    """Verify raise_union_ambiguous_error produces a well-formed DeserializationError card."""
    fitting = ", ".join(describe_annotation(member) for member in matched)

    def raising_wrapper(target_location):
        raise_union_ambiguous_error(target_location, annotation, data, matched)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_UNION_AMBIGUOUS",
        label=label,
        value=data,
        problem=f"The data fits several members equally well: {fitting}.",
        expected="Data that fits exactly one member, or one that is exactly the data's own type.",
        how_to_fix=(
            "Narrow the union to members that cannot both accept the same data.",
            f"Or register a handler for this exact annotation: register_type({annotation!r}, from_func=...).",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
