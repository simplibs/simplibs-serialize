from typing import Annotated, Literal, NewType

import pytest

from simplibs.serialize.logic.registry._helpers import is_registrable_type


class Point:
    """A user class."""


UserId = NewType("UserId", int)


@pytest.mark.parametrize(
    "target",
    [Point, int, list[int], int | None, Annotated[int, 1], Literal["a"], UserId],
    ids=["user_class", "builtin", "subscripted", "optional", "annotated", "literal", "newtype"],
)
def test_true_for_what_a_caller_writes_as_a_target(target):
    assert is_registrable_type(target) is True


@pytest.mark.parametrize(
    "target",
    ["Point", Point(), None, 5, lambda value: value],
    ids=["text", "instance", "none", "number", "plain_function"],
)
def test_false_for_what_the_lookup_could_never_meet(target):
    assert is_registrable_type(target) is False
