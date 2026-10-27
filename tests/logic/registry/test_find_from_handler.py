from datetime import datetime
from typing import NewType

from simplibs.serialize.logic.registry import find_from_handler, register_type, unregister_type
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_FROM_HANDLERS


class Point:
    """A custom class."""


class Point3D(Point):
    """A subclass of the custom class."""


UserId = NewType("UserId", int)


def test_finds_a_builtin_handler():
    assert find_from_handler(datetime) is BUILTIN_FROM_HANDLERS[datetime]


def test_an_unknown_annotation_has_no_handler():
    assert find_from_handler(Point) is None
    assert find_from_handler(list[int]) is None


def test_reads_the_live_table_so_a_registration_is_seen():
    handler = lambda data, target: target()

    register_type(Point, from_func=handler)

    assert find_from_handler(Point) is handler
    assert find_from_handler(Point3D) is handler


def test_a_subscripted_annotation_and_a_newtype_are_found_exactly():
    ints = lambda data, target: list(data)
    user_id = lambda data, target: int(data)

    register_type(list[int], from_func=ints)
    register_type(UserId, from_func=user_id)

    assert find_from_handler(list[int]) is ints
    assert find_from_handler(list[str]) is None
    assert find_from_handler(UserId) is user_id


def test_a_replaced_builtin_is_seen_and_restored_by_unregister():
    handler = lambda data, target: target.now()

    register_type(datetime, from_func=handler)
    assert find_from_handler(datetime) is handler

    unregister_type(datetime)
    assert find_from_handler(datetime) is BUILTIN_FROM_HANDLERS[datetime]
