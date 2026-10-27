from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Annotated, Any, Final, Generic, Literal, NamedTuple, NewType, TypedDict, TypeVar

import pytest

from simplibs.serialize import DeserializationError, register_type
from simplibs.serialize.logic.deserializer._builders import build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


T = TypeVar("T")
UserId = NewType("UserId", int)


class Color(Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


class Port(int):
    """An int subclass."""


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Box(Generic[T]):
    item: T


class Pair(NamedTuple):
    a: int
    b: int


class Options(TypedDict):
    name: str


class Unregistered:
    """Nothing knows this class."""


def _context(strict=True) -> DeserializeContext:
    return DeserializeContext(strict=strict, build_value=build_value)


def _build(data, annotation, location=()):
    return build_value(data, annotation, location, _context())


# ---------- 1. anything goes ----------

@pytest.mark.parametrize("annotation", [Any, object], ids=["Any", "object"])
@pytest.mark.parametrize(
    "data",
    [None, 5, "a", [1], {"a": 1}, 1.5, True],
    ids=["none", "int", "text", "list", "dict", "float", "bool"],
)
def test_any_and_object_return_the_data_as_it_is(annotation, data):
    assert _build(data, annotation) is data


# ---------- 2. a handler ----------

@pytest.mark.parametrize(
    "data, annotation, expected",
    [
        pytest.param("2026-01-02", date, date(2026, 1, 2), id="date"),
        pytest.param("2026-01-02T03:04:05", datetime, datetime(2026, 1, 2, 3, 4, 5), id="datetime"),
        pytest.param("red", Color, Color.RED, id="enum"),
        pytest.param(1, Level, Level.LOW, id="int_enum"),
    ],
)
def test_a_builtin_handler_builds_the_value(data, annotation, expected):
    assert _build(data, annotation) == expected


def test_a_registered_handler_builds_a_custom_class():
    register_type(Unregistered, from_func=lambda data, annotation: ("built", data))

    assert _build(5, Unregistered) == ("built", 5)


def test_a_handler_for_an_exact_annotation_wins_over_the_general_rule():
    register_type(list[int], from_func=lambda data, annotation: ("custom", data))

    assert _build([1], list[int]) == ("custom", [1])
    assert _build(["a"], list[str]) == ["a"]


def test_a_handler_for_a_newtype_is_found_before_the_alias_rule():
    register_type(UserId, from_func=lambda data, annotation: ("custom", data))

    assert _build(5, UserId) == ("custom", 5)


def test_a_handler_for_a_class_never_receives_none():
    with pytest.raises(DeserializationError) as caught:
        _build(None, date, ("when",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.when"


def test_a_handler_for_something_that_is_not_a_class_may_receive_none():
    register_type(UserId, from_func=lambda data, annotation: ("custom", data))

    assert _build(None, UserId) == ("custom", None)


def test_a_failing_handler_is_a_build_failed_card_at_the_location():
    with pytest.raises(DeserializationError) as caught:
        _build("not a date", date, ("when",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.when"


# ---------- 3. none ----------

@pytest.mark.parametrize("annotation", [None, type(None)], ids=["None", "NoneType"])
def test_none_is_built_for_none(annotation):
    assert _build(None, annotation) is None


@pytest.mark.parametrize("annotation", [None, type(None)], ids=["None", "NoneType"])
def test_anything_else_is_a_wrong_type_card_for_none(annotation):
    with pytest.raises(DeserializationError) as caught:
        _build(0, annotation, ("n",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.n"


# ---------- None for every kind of annotation ----------

@pytest.mark.parametrize(
    "annotation, error_name",
    [
        pytest.param(int, "DESERIALIZE_WRONG_TYPE", id="int"),
        pytest.param(str, "DESERIALIZE_WRONG_TYPE", id="str"),
        pytest.param(float, "DESERIALIZE_WRONG_TYPE", id="float"),
        pytest.param(bool, "DESERIALIZE_WRONG_TYPE", id="bool"),
        pytest.param(Port, "DESERIALIZE_WRONG_TYPE", id="int_subclass"),
        pytest.param(list[int], "DESERIALIZE_WRONG_TYPE", id="list"),
        pytest.param(dict[str, int], "DESERIALIZE_WRONG_TYPE", id="dict"),
        pytest.param(tuple[int, ...], "DESERIALIZE_WRONG_TYPE", id="tuple"),
        pytest.param(set[int], "DESERIALIZE_WRONG_TYPE", id="set"),
        pytest.param(Point, "DESERIALIZE_WRONG_TYPE", id="dataclass"),
        pytest.param(Pair, "DESERIALIZE_WRONG_TYPE", id="named_tuple"),
        pytest.param(Options, "DESERIALIZE_WRONG_TYPE", id="typed_dict"),
        pytest.param(date, "DESERIALIZE_WRONG_TYPE", id="class_with_a_handler"),
        pytest.param(Color, "DESERIALIZE_WRONG_TYPE", id="enum"),
        pytest.param(UserId, "DESERIALIZE_WRONG_TYPE", id="newtype"),
        pytest.param(Final[int], "DESERIALIZE_WRONG_TYPE", id="final"),
        pytest.param(Annotated[int, "doc"], "DESERIALIZE_WRONG_TYPE", id="annotated"),
        pytest.param(Literal["a"], "DESERIALIZE_LITERAL_MISMATCH", id="literal"),
        pytest.param(int | str, "DESERIALIZE_UNION_NO_MATCH", id="union_without_none"),
    ],
)
def test_none_is_accepted_for_nothing_that_does_not_ask_for_it(annotation, error_name):
    with pytest.raises(DeserializationError) as caught:
        _build(None, annotation, ("n",))

    assert caught.value.error_name == error_name
    assert caught.value.label == "$.n"


@pytest.mark.parametrize(
    "annotation",
    [Any, int | None, Literal[None], Annotated[int | None, "doc"], list[int] | None],
    ids=["Any", "optional", "literal_none", "annotated_optional", "optional_list"],
)
def test_none_is_accepted_where_the_annotation_asks_for_it(annotation):
    assert _build(None, annotation) is None


# ---------- 4. primitives ----------

@pytest.mark.parametrize(
    "data, annotation",
    [(5, int), ("a", str), (1.5, float), (True, bool), (1, float)],
    ids=["int", "str", "float", "bool", "int_for_float"],
)
def test_a_primitive_is_checked_and_built(data, annotation):
    assert _build(data, annotation) == data


def test_a_subclass_of_a_primitive_is_built_as_the_subclass():
    result = _build(8080, Port)

    assert result == 8080
    assert type(result) is Port


def test_a_primitive_of_the_wrong_kind_is_a_wrong_type_card():
    with pytest.raises(DeserializationError) as caught:
        _build("abc", int, ("port",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.port"


# ---------- 5. containers, unions, Annotated, Literal ----------

@pytest.mark.parametrize(
    "data, annotation, expected",
    [
        pytest.param([1, 2], list[int], [1, 2], id="list"),
        pytest.param([1, 1], set[int], {1}, id="set"),
        pytest.param({"a": 1}, dict[str, int], {"a": 1}, id="dict"),
        pytest.param([1, "a"], tuple[int, str], (1, "a"), id="tuple"),
        pytest.param(5, int | str, 5, id="union"),
        pytest.param(5, Annotated[int, "doc"], 5, id="annotated"),
        pytest.param("a", Literal["a", "b"], "a", id="literal"),
        pytest.param(5, Final[int], 5, id="final"),
        pytest.param([{"x": 1, "y": 2}], list[Point], [Point(1, 2)], id="list_of_dataclasses"),
    ],
)
def test_the_table_decides_by_the_origin_of_the_annotation(data, annotation, expected):
    assert _build(data, annotation) == expected


def test_an_annotated_with_unhashable_metadata_still_works():
    assert _build(5, Annotated[int, [1, 2]]) == 5


# ---------- 6. aliases ----------

def test_a_newtype_is_built_as_what_it_wraps():
    assert _build(5, UserId) == 5
    with pytest.raises(DeserializationError):
        _build("x", UserId)


# ---------- 7. classes with a structure of their own ----------

def test_a_dataclass():
    assert _build({"x": 1, "y": 2}, Point) == Point(1, 2)


def test_a_generic_dataclass_with_its_type_argument():
    assert _build({"item": 1}, Box[int]) == Box(1)
    with pytest.raises(DeserializationError):
        _build({"item": "x"}, Box[int])


def test_a_named_tuple():
    assert _build({"a": 1, "b": 2}, Pair) == Pair(1, 2)
    assert _build([1, 2], Pair) == Pair(1, 2)


def test_a_typed_dict():
    assert _build({"name": "ann"}, Options) == {"name": "ann"}


# ---------- 8. nothing recognized ----------

@pytest.mark.parametrize(
    "annotation",
    [Callable[..., int], Unregistered, complex, "int", 5],
    ids=["callable", "unregistered_class", "complex", "text", "number"],
)
def test_an_annotation_nothing_knows_is_an_unsupported_annotation_card(annotation):
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1}, annotation, ("n",))

    assert caught.value.error_name == "DESERIALIZE_UNSUPPORTED_ANNOTATION"
    assert caught.value.label == "$.n"
    assert caught.value.value == annotation


# ---------- the order of the steps ----------

def test_a_bool_is_not_turned_into_an_int_by_the_primitive_step():
    with pytest.raises(DeserializationError):
        _build(True, int)


def test_a_list_of_dataclasses_is_a_list_first_then_the_dataclass():
    with pytest.raises(DeserializationError) as caught:
        _build([{"x": 1, "y": "bad"}], list[Point])

    assert caught.value.label == "$[0].y"


# ---------- unhashable annotations ----------

def test_an_unhashable_annotation_triggers_unsupported_annotation_error():
    # Passing an unhashable annotation raises a TypeError during the table lookup,
    # which should be handled and reported as an unsupported annotation.
    with pytest.raises(DeserializationError) as caught:
        _build(1, [int], ("n",))

    assert caught.value.error_name == "DESERIALIZE_UNSUPPORTED_ANNOTATION"
    assert caught.value.label == "$.n"
    assert caught.value.value == [int]