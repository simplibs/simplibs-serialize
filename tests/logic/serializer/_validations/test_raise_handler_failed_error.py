import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_handler_failed_error


class _Point:
    """A value whose handler fails."""


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_VALUES = [
    pytest.param(_Point(), "_Point", id="object"),
    pytest.param(5, "int", id="integer"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("obj, type_name", _VALUES)
@pytest.mark.parametrize(
    "caught",
    [AttributeError("no attribute x"), ZeroDivisionError("division by zero")],
    ids=["AttributeError", "ZeroDivisionError"],
)
def test_raise_handler_failed_error_contract(subtests, caught, obj, type_name, location, label) -> None:
    """Verify raise_handler_failed_error produces a well-formed SerializationError card."""

    def raising_wrapper(target_location):
        raise_handler_failed_error(target_location, obj, caught)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=SerializationError,
        error_name="SERIALIZE_HANDLER_FAILED",
        label=label,
        value=obj,
        problem=f"The handler for '{type_name}' raised {type(caught).__name__}: {caught}",
        expected="A handler that returns a value for every object of its type.",
        how_to_fix=(
            "Fix the handler registered with register_type() (or the `default=` function).",
            "The original exception is attached as the cause of this one.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as ValueError and keep the handler's exception as its cause
    assert isinstance(exc, ValueError)
    assert exc.__cause__ is caught
