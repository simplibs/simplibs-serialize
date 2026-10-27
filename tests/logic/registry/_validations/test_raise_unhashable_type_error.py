from typing import Annotated

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize.logic.registry._validations import raise_unhashable_type_error


@pytest.mark.parametrize(
    "type_",
    [Annotated[int, [1, 2]], [int]],
    ids=["annotated_with_list", "plain_list"],
)
def test_raise_unhashable_type_error_contract(subtests, type_) -> None:
    """Verify raise_unhashable_type_error produces a well-formed ParamError card."""

    def raising_wrapper(target):
        raise_unhashable_type_error(target)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(type_,),
        exception_type=ParamError,
        error_name="SERIALIZE_REGISTER_UNHASHABLE_TYPE",
        label="type_",
        value=type_,
        problem=f"{type_!r} is not hashable, so it cannot be a key of the registry.",
        expected="A hashable class or annotation.",
        how_to_fix=(
            "Register the plain class instead of the annotated one.",
            "Use only hashable objects as the metadata of `Annotated[...]`.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
