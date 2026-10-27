import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_union_no_match_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_CASES = [
    pytest.param(str | list[str], 5, "an integer", id="integer"),
    pytest.param(int | None, "x", "text", id="text"),
    pytest.param(int | str, {"a": 1}, "an object", id="object"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation, data, kind", _CASES)
@pytest.mark.parametrize("has_closest", [False, True], ids=["no_closest", "with_closest"])
def test_raise_union_no_match_error_contract(
    subtests, has_closest, annotation, data, kind, location, label
) -> None:
    """Verify raise_union_no_match_error produces a well-formed DeserializationError card."""
    wanted = describe_annotation(annotation)
    closest = DeserializationError(message="the closest failure") if has_closest else None

    def raising_wrapper(target_location):
        raise_union_no_match_error(target_location, annotation, data, closest)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_UNION_NO_MATCH",
        label=label,
        value=data,
        problem=f"Got {kind}, which fits none of: {wanted}.",
        expected=f"Data that fits one of: {wanted}.",
        how_to_fix="Correct the data so that it fits one of the members of the union.",
        exception=TypeError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)

    # The failure of the closest member becomes the cause; without one there is no cause
    assert exc.__cause__ is closest
