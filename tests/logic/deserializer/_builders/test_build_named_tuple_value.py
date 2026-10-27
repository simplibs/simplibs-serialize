from collections import namedtuple
from typing import NamedTuple

import pytest

from simplibs.serialize.exceptions import DeserializationError, SerializeError
from simplibs.serialize.logic.deserializer._builders import build_named_tuple_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


class Point(NamedTuple):
    x: int
    y: int


class WithDefaults(NamedTuple):
    a: int
    b: int = 5
    c: str = "z"


class Line(NamedTuple):
    start: Point
    end: Point


class Unresolvable(NamedTuple):
    a: "DoesNotExist"  # noqa: F821


Untyped = namedtuple("Untyped", ["x", "y"])


def _real_context(strict=True) -> DeserializeContext:
    return DeserializeContext(strict=strict, build_value=build_value)


def _fake_context(strict=True):
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_build_value(data, annotation, location, context):
        calls.append((data, annotation, location))
        return data

    return DeserializeContext(strict=strict, build_value=fake_build_value), calls


def _build(data, annotation, location=(), strict=True):
    return build_named_tuple_value(data, annotation, location, _real_context(strict))


# ---------- by name and by position ----------

def test_an_object_is_read_by_field_name():
    result = _build({"x": 1, "y": 2}, Point)

    assert result == Point(1, 2)
    assert type(result) is Point


def test_the_order_of_keys_in_an_object_does_not_matter():
    assert _build({"y": 2, "x": 1}, Point) == Point(1, 2)


def test_a_list_is_read_by_position():
    result = _build([1, 2], Point)

    assert result == Point(1, 2)
    assert type(result) is Point


def test_a_tuple_of_data_is_read_by_position():
    assert _build((1, 2), Point) == Point(1, 2)


def test_nested_named_tuples_by_name_and_by_position():
    assert _build({"start": {"x": 1, "y": 2}, "end": [3, 4]}, Line) == Line(Point(1, 2), Point(3, 4))


# ---------- defaults ----------

def test_an_object_may_leave_out_a_field_with_a_default_anywhere():
    assert _build({"a": 1, "c": "q"}, WithDefaults) == WithDefaults(1, 5, "q")


@pytest.mark.parametrize(
    "data, expected",
    [
        pytest.param([1], WithDefaults(1, 5, "z"), id="only_the_required"),
        pytest.param([1, 2], WithDefaults(1, 2, "z"), id="one_default_given"),
        pytest.param([1, 2, "q"], WithDefaults(1, 2, "q"), id="all_given"),
    ],
)
def test_a_list_may_leave_out_fields_with_defaults_from_the_right_end(data, expected):
    assert _build(data, WithDefaults) == expected


# ---------- wrong length ----------

@pytest.mark.parametrize("data", [[1], [], [1, 2, 3]], ids=["too_short", "empty", "too_long"])
def test_a_list_of_the_wrong_length_is_a_wrong_length_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, Point, ("pt",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_LENGTH"
    assert caught.value.label == "$.pt"
    assert caught.value.value == data


def test_a_list_with_defaults_has_a_range_of_allowed_lengths():
    with pytest.raises(DeserializationError) as caught:
        _build([], WithDefaults)

    assert caught.value.error_name == "DESERIALIZE_WRONG_LENGTH"
    assert "1 to 3 items" in str(caught.value.problem)


# ---------- missing and unknown ----------

def test_a_missing_field_is_an_error_naming_every_missing_one():
    with pytest.raises(DeserializationError) as caught:
        _build({}, Point, ("pt",))

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.label == "$.pt"
    assert caught.value.value == ["x", "y"]


def test_an_unknown_key_is_an_error_when_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"x": 1, "y": 2, "z": 3}, Point)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert caught.value.value == ["z"]


def test_an_unknown_key_is_ignored_when_not_strict():
    assert _build({"x": 1, "y": 2, "z": 3}, Point, strict=False) == Point(1, 2)


def test_a_typo_is_reported_as_unknown_with_what_is_missing():
    with pytest.raises(DeserializationError) as caught:
        _build({"x": 1, "yy": 2}, Point)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert "Required but absent: 'y'" in str(caught.value.problem)


def test_a_typo_is_a_missing_field_when_not_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"x": 1, "yy": 2}, Point, strict=False)

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.value == ["y"]


# ---------- data of another kind ----------

@pytest.mark.parametrize("data", ["abc", 5, None, True], ids=["text", "int", "none", "bool"])
def test_data_that_is_neither_an_object_nor_a_list_is_a_wrong_type_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, Point, ("pt",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.pt"
    assert caught.value.value == data


# ---------- types of the fields ----------

def test_a_field_that_does_not_fit_is_located_by_name_in_an_object():
    with pytest.raises(DeserializationError) as caught:
        _build({"x": "bad", "y": 2}, Point, ("pt",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.pt.x"


def test_a_field_that_does_not_fit_is_located_by_index_in_a_list():
    with pytest.raises(DeserializationError) as caught:
        _build([1, "bad"], Point, ("pt",))

    assert caught.value.label == "$.pt[1]"


def test_every_field_is_built_against_its_annotation():
    context, calls = _fake_context()

    build_named_tuple_value({"x": 1, "y": 2}, Point, ("pt",), context)

    assert calls == [(1, int, ("pt", "x")), (2, int, ("pt", "y"))]


# ---------- collections.namedtuple has no types ----------

def test_a_namedtuple_takes_any_value_in_every_field():
    assert _build({"x": "a", "y": [1]}, Untyped) == Untyped("a", [1])
    assert _build(["a", None], Untyped) == Untyped("a", None)


# ---------- annotations that cannot be resolved ----------

def test_an_unresolvable_annotation_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1}, Unresolvable, ("row",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.row"
    assert isinstance(caught.value.__cause__, NameError)


# ---------- construction errors ----------

BaseFailingTuple = namedtuple("BaseFailingTuple", ["x"])

class FailingNamedTuple(BaseFailingTuple):
    def __new__(cls, x):
        if x == -999:
            raise ValueError("Custom construction failure")
        return super().__new__(cls, x)


def test_a_named_tuple_construction_failure_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        _build({"x": -999}, FailingNamedTuple, ("pt",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.pt"
    assert isinstance(caught.value.__cause__, ValueError)


def test_a_named_tuple_serialize_error_is_reraised_directly():
    class SerializeErrorNamedTuple(BaseFailingTuple):
        def __new__(cls, x):
            raise SerializeError("Custom serialize error")

    with pytest.raises(SerializeError) as caught:
        _build({"x": 1}, SerializeErrorNamedTuple, ("pt",))

    assert "Custom serialize error" in str(caught.value)