from datetime import datetime
from typing import Annotated

from simplibs.serialize.logic.registry import find_from_handler, find_to_handler, register_type, unregister_type
from simplibs.serialize.logic.registry._handlers.active import FROM_HANDLERS, TO_HANDLERS
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_FROM_HANDLERS, BUILTIN_TO_HANDLERS


class Point:
    """A custom class."""


def _to(obj):
    return 0


def _from(data, target):
    return target()


def test_a_registered_type_is_removed_in_both_directions():
    register_type(Point, to_func=_to, from_func=_from)

    assert unregister_type(Point) is True
    assert Point not in TO_HANDLERS
    assert Point not in FROM_HANDLERS


def test_a_type_registered_in_one_direction_only_is_removed_too():
    register_type(Point, from_func=_from)

    assert unregister_type(Point) is True
    assert Point not in FROM_HANDLERS


def test_a_subscripted_annotation_is_removed():
    register_type(list[int], from_func=_from)

    assert unregister_type(list[int]) is True
    assert find_from_handler(list[int]) is None


def test_a_replaced_builtin_comes_back():
    register_type(datetime, to_func=_to, from_func=_from)

    assert unregister_type(datetime) is True
    assert find_to_handler(datetime) is BUILTIN_TO_HANDLERS[datetime]
    assert find_from_handler(datetime) is BUILTIN_FROM_HANDLERS[datetime]


def test_replacing_one_direction_leaves_the_other_builtin_side_alone():
    register_type(datetime, to_func=_to)

    assert FROM_HANDLERS[datetime] is BUILTIN_FROM_HANDLERS[datetime]
    assert unregister_type(datetime) is True
    assert TO_HANDLERS[datetime] is BUILTIN_TO_HANDLERS[datetime]
    assert FROM_HANDLERS[datetime] is BUILTIN_FROM_HANDLERS[datetime]


def test_an_unknown_type_returns_false():
    assert unregister_type(Point) is False


def test_an_untouched_builtin_returns_false():
    assert unregister_type(datetime) is False
    assert find_to_handler(datetime) is BUILTIN_TO_HANDLERS[datetime]


def test_calling_it_twice_is_safe():
    register_type(Point, to_func=_to)

    assert unregister_type(Point) is True
    assert unregister_type(Point) is False


def test_an_unhashable_annotation_returns_false():
    assert unregister_type(Annotated[int, [1, 2]]) is False
