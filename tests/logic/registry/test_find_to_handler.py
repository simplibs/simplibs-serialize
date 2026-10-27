from datetime import datetime
from pathlib import Path

from simplibs.serialize.logic.registry import find_to_handler, register_type, unregister_type
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_TO_HANDLERS


class Point:
    """A custom class."""


class Point3D(Point):
    """A subclass of the custom class."""


def test_finds_a_builtin_handler():
    assert find_to_handler(datetime) is BUILTIN_TO_HANDLERS[datetime]


def test_finds_a_builtin_handler_through_a_base_class():
    assert find_to_handler(type(Path("a/b"))) is not None


def test_an_unknown_class_has_no_handler():
    assert find_to_handler(Point) is None


def test_reads_the_live_table_so_a_registration_is_seen():
    handler = lambda obj: {"x": 1}

    register_type(Point, to_func=handler)

    assert find_to_handler(Point) is handler
    assert find_to_handler(Point3D) is handler


def test_a_replaced_builtin_is_seen_and_restored_by_unregister():
    handler = lambda obj: 0

    register_type(datetime, to_func=handler)
    assert find_to_handler(datetime) is handler

    unregister_type(datetime)
    assert find_to_handler(datetime) is BUILTIN_TO_HANDLERS[datetime]
