from datetime import date, datetime
from enum import Enum
from pathlib import Path, PurePath
from typing import Annotated

import pytest

from simplibs.serialize.logic.registry._helpers import find_handler


class Base:
    pass


class Middle(Base):
    pass


class Leaf(Middle):
    pass


class Color(str, Enum):
    RED = "red"


def test_exact_match():
    assert find_handler({Leaf: "leaf"}, Leaf) == "leaf"


def test_a_subclass_finds_the_handler_of_its_base():
    assert find_handler({PurePath: "path"}, type(Path("a/b"))) == "path"


def test_the_nearest_base_wins():
    handlers = {Base: "base", Middle: "middle"}

    assert find_handler(handlers, Leaf) == "middle"


def test_a_class_with_its_own_entry_wins_over_its_base():
    handlers = {Base: "base", Leaf: "leaf"}

    assert find_handler(handlers, Leaf) == "leaf"


def test_datetime_has_its_own_entry_next_to_date():
    handlers = {date: "date", datetime: "datetime"}

    assert find_handler(handlers, datetime) == "datetime"
    assert find_handler(handlers, date) == "date"


def test_datetime_without_an_entry_of_its_own_falls_back_on_date():
    assert find_handler({date: "date"}, datetime) == "date"


def test_a_base_does_not_find_the_handler_of_its_subclass():
    assert find_handler({Leaf: "leaf"}, Base) is None


def test_a_str_enum_reaches_the_enum_entry():
    assert find_handler({Enum: "enum"}, Color) == "enum"


def test_a_subscripted_annotation_is_matched_exactly_only():
    handlers = {list[int]: "ints", list: "list"}

    assert find_handler(handlers, list[int]) == "ints"
    assert find_handler(handlers, list[str]) is None


def test_an_unhashable_annotation_finds_nothing_instead_of_failing():
    assert find_handler({int: "int"}, Annotated[int, [1, 2]]) is None


@pytest.mark.parametrize("target", [Leaf, int, "text", None], ids=["class", "builtin", "text", "none"])
def test_nothing_registered_finds_nothing(target):
    assert find_handler({}, target) is None
