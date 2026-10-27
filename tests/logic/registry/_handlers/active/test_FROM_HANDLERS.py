from datetime import datetime

from simplibs.serialize.logic.registry._handlers.active import FROM_HANDLERS
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_FROM_HANDLERS


class Point:
    """A class that is not built in."""


def test_starts_as_a_copy_of_the_builtin_table():
    assert dict(FROM_HANDLERS) == dict(BUILTIN_FROM_HANDLERS)


def test_is_a_separate_mutable_dict():
    assert isinstance(FROM_HANDLERS, dict)
    assert FROM_HANDLERS is not BUILTIN_FROM_HANDLERS


def test_writing_into_it_leaves_the_builtin_table_alone():
    original = BUILTIN_FROM_HANDLERS[datetime]

    FROM_HANDLERS[Point] = lambda data, target: target()
    FROM_HANDLERS[datetime] = lambda data, target: target.now()

    assert Point not in BUILTIN_FROM_HANDLERS
    assert BUILTIN_FROM_HANDLERS[datetime] is original
