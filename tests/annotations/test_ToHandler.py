from collections.abc import Callable
from typing import Any

from simplibs.serialize.annotations import ToHandler


def test_is_a_callable_taking_the_object():
    assert ToHandler == Callable[[Any], Any]
