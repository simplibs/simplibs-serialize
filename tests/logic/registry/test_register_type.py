from datetime import datetime
from typing import Annotated, NewType

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import deserialize, serialize
from simplibs.serialize.logic.registry import find_from_handler, find_to_handler, register_type
from simplibs.serialize.logic.registry._handlers.active import FROM_HANDLERS, TO_HANDLERS
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_FROM_HANDLERS, BUILTIN_TO_HANDLERS
from simplibs.serialize.testing import assert_round_trip


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)


class Point3D(Point):
    """A subclass of the custom class."""


UserId = NewType("UserId", int)


def _to_point(point):
    return {"x": point.x, "y": point.y}


def _from_point(data, target):
    return target(data["x"], data["y"])


def _tables():
    """A snapshot of both live tables."""
    return dict(TO_HANDLERS), dict(FROM_HANDLERS)


# ---------- what is stored ----------

def test_both_handlers_are_stored():
    register_type(Point, to_func=_to_point, from_func=_from_point)

    assert TO_HANDLERS[Point] is _to_point
    assert FROM_HANDLERS[Point] is _from_point


def test_only_the_given_handler_is_stored():
    register_type(Point, to_func=_to_point)

    assert TO_HANDLERS[Point] is _to_point
    assert Point not in FROM_HANDLERS


def test_from_func_alone_is_enough_for_a_subscripted_annotation():
    register_type(list[int], from_func=_from_point)

    assert FROM_HANDLERS[list[int]] is _from_point
    assert list[int] not in TO_HANDLERS


def test_from_func_alone_is_enough_for_a_newtype():
    register_type(UserId, from_func=_from_point)

    assert FROM_HANDLERS[UserId] is _from_point


def test_the_builtin_tables_are_never_touched():
    register_type(Point, to_func=_to_point, from_func=_from_point)
    register_type(datetime, to_func=_to_point, from_func=_from_point)

    assert Point not in BUILTIN_TO_HANDLERS
    assert Point not in BUILTIN_FROM_HANDLERS
    assert BUILTIN_TO_HANDLERS[datetime] is not _to_point
    assert BUILTIN_FROM_HANDLERS[datetime] is not _from_point


def test_a_builtin_handler_can_be_replaced():
    register_type(datetime, to_func=lambda obj: obj.timestamp())

    assert find_to_handler(datetime) is TO_HANDLERS[datetime]
    assert find_to_handler(datetime) is not BUILTIN_TO_HANDLERS[datetime]


def test_a_subclass_is_found_through_its_base():
    register_type(Point, to_func=_to_point, from_func=_from_point)

    assert find_to_handler(Point3D) is _to_point
    assert find_from_handler(Point3D) is _from_point


# ---------- a wrong call raises and stores nothing ----------

def test_no_handler_raises():
    before = _tables()

    with pytest.raises(ParamError) as caught:
        register_type(Point)

    assert caught.value.error_name == "SERIALIZE_REGISTER_NO_HANDLER"
    assert _tables() == before


@pytest.mark.parametrize("type_", ["Point", Point(1, 2), None, 5], ids=["text", "instance", "none", "number"])
def test_something_that_is_not_a_type_raises(type_):
    before = _tables()

    with pytest.raises(ParamError) as caught:
        register_type(type_, to_func=_to_point, from_func=_from_point)

    assert caught.value.error_name == "SERIALIZE_REGISTER_NOT_A_TYPE"
    assert _tables() == before


def test_an_unhashable_annotation_raises():
    before = _tables()

    with pytest.raises(ParamError) as caught:
        register_type(Annotated[int, [1, 2]], from_func=_from_point)

    assert caught.value.error_name == "SERIALIZE_REGISTER_UNHASHABLE_TYPE"
    assert _tables() == before


@pytest.mark.parametrize("type_", [list[int], UserId, int | None], ids=["subscripted", "newtype", "union"])
def test_to_func_for_something_that_is_not_a_class_raises(type_):
    before = _tables()

    with pytest.raises(ParamError) as caught:
        register_type(type_, to_func=_to_point, from_func=_from_point)

    assert caught.value.error_name == "SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS"
    assert _tables() == before


# ---------- with serialize and deserialize ----------

def test_serialize_and_deserialize_use_the_registered_type():
    register_type(Point, to_func=_to_point, from_func=_from_point)

    assert serialize(Point(1, 2)) == {"x": 1, "y": 2}
    assert deserialize({"x": 1, "y": 2}, Point) == Point(1, 2)


def test_round_trip_of_a_registered_type_alone_and_inside_containers(subtests):
    register_type(Point, to_func=_to_point, from_func=_from_point)

    assert_round_trip(subtests, Point(1, 2))
    assert_round_trip(subtests, [Point(1, 2), Point(3, 4)], list[Point])
    assert_round_trip(subtests, {"a": Point(1, 2)}, dict[str, Point])
