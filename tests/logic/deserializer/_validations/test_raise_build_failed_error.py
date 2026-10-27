import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.logic.deserializer._validations import raise_build_failed_error


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation", [int, list[int] | None], ids=["int", "list_or_none"])
@pytest.mark.parametrize(
    "caught",
    [ValueError("bad value"), TypeError("bad type")],
    ids=["ValueError", "TypeError"],
)
def test_raise_build_failed_error_contract(subtests, caught, annotation, location, label) -> None:
    """Verify raise_build_failed_error produces a well-formed DeserializationError card."""
    wanted = describe_annotation(annotation)

    def raising_wrapper(target_location):
        raise_build_failed_error(target_location, annotation, caught)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_BUILD_FAILED",
        label=label,
        problem=f"Building {wanted} failed: {type(caught).__name__}: {caught}",
        expected=f"Data that {wanted} can be built from.",
        how_to_fix=(
            "Correct the data at this location.",
            "If the type is your own: check its handler or constructor. "
            "The original exception is attached as the cause.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as ValueError and keep the original exception as its cause
    assert isinstance(exc, ValueError)
    assert exc.__cause__ is caught
