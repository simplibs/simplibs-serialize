from datetime import datetime

from simplibs.serialize.logic.registry._handlers.active import TO_HANDLERS
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_TO_HANDLERS


class Point:
    """A class that is not built in."""


def test_starts_as_a_copy_of_the_builtin_table():
    assert dict(TO_HANDLERS) == dict(BUILTIN_TO_HANDLERS)


def test_is_a_separate_mutable_dict():
    assert isinstance(TO_HANDLERS, dict)
    assert TO_HANDLERS is not BUILTIN_TO_HANDLERS


def test_writing_into_it_leaves_the_builtin_table_alone():
    original = BUILTIN_TO_HANDLERS[datetime]

    TO_HANDLERS[Point] = str
    TO_HANDLERS[datetime] = str

    assert Point not in BUILTIN_TO_HANDLERS
    assert BUILTIN_TO_HANDLERS[datetime] is original
