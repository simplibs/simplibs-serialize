from enum import Enum
from typing import Annotated

import pytest

from simplibs.serialize.logic.registry._helpers import is_plain_class


class Point:
    """A user class."""


class Color(Enum):
    RED = 1


@pytest.mark.parametrize("target", [int, Point, Color], ids=["builtin", "user_class", "enum_class"])
def test_true_for_a_real_class(target):
    assert is_plain_class(target) is True


@pytest.mark.parametrize(
    "target",
    [list[int], int | str, Annotated[int, 1], Point(), Color.RED, "int", None, 5],
    ids=["subscripted", "union", "annotated", "instance", "enum_member", "text", "none", "number"],
)
def test_false_for_everything_else(target):
    assert is_plain_class(target) is False
