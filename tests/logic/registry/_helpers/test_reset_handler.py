from types import MappingProxyType
from typing import Annotated

from simplibs.serialize.logic.registry._helpers import reset_handler


class Point:
    """A custom class."""


def _shipped(): return "shipped"
def _replaced(): return "replaced"
def _custom(): return "custom"


def test_a_pure_registration_is_removed():
    live = {Point: _custom}

    assert reset_handler(live, MappingProxyType({}), Point) is True
    assert Point not in live


def test_a_replaced_builtin_is_restored():
    live = {int: _replaced}

    assert reset_handler(live, MappingProxyType({int: _shipped}), int) is True
    assert live[int] is _shipped


def test_a_builtin_that_is_missing_from_the_live_table_comes_back():
    live = {}

    assert reset_handler(live, MappingProxyType({int: _shipped}), int) is True
    assert live[int] is _shipped


def test_an_untouched_builtin_changes_nothing():
    live = {int: _shipped}

    assert reset_handler(live, MappingProxyType({int: _shipped}), int) is False
    assert live == {int: _shipped}


def test_an_unknown_key_changes_nothing():
    live = {int: _shipped}

    assert reset_handler(live, MappingProxyType({int: _shipped}), Point) is False
    assert live == {int: _shipped}


def test_an_unhashable_key_changes_nothing():
    live = {int: _shipped}

    assert reset_handler(live, MappingProxyType({int: _shipped}), Annotated[int, [1]]) is False
    assert live == {int: _shipped}
