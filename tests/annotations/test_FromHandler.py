from collections.abc import Callable
from typing import Any

from simplibs.serialize.annotations import FromHandler


def test_is_a_callable_taking_the_data_and_the_annotation():
    assert FromHandler == Callable[[Any, Any], Any]
