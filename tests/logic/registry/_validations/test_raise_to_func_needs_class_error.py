import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize.logic.registry._validations import raise_to_func_needs_class_error


@pytest.mark.parametrize("type_", [list[int], int | None], ids=["subscripted_list", "union"])
def test_raise_to_func_needs_class_error_contract(subtests, type_) -> None:
    """Verify raise_to_func_needs_class_error produces a well-formed ParamError card."""

    def raising_wrapper(target):
        raise_to_func_needs_class_error(target)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(type_,),
        exception_type=ParamError,
        error_name="SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS",
        label="to_func",
        value=type_,
        problem=(
            "`to_func` is found through the class of the object being serialized, "
            f"so it could never run for {type_!r}."
        ),
        expected="A plain class as `type_` whenever `to_func` is given.",
        how_to_fix=(
            "Register `to_func` on the class itself, e.g. `list` or `Point`.",
            "Keep `from_func` alone for an annotation such as `list[int]`.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
