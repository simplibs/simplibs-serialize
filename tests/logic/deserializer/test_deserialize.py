import copy
from collections import OrderedDict, deque
from collections.abc import Callable, Mapping, Sequence, Set
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, IntEnum
from fractions import Fraction
from ipaddress import IPv4Address
from pathlib import PurePosixPath
from typing import Annotated, Any, Generic, Literal, NamedTuple, NewType, Optional, TypedDict, TypeVar
from uuid import UUID

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import DeserializationError, deserialize, serialized_field
from simplibs.serialize.testing import assert_round_trip


T = TypeVar("T")
UserId = NewType("UserId", int)


class Color(Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Server:
    host: str
    port: int


@dataclass
class Config:
    servers: list[Server]
    tags: set[str] = field(default_factory=set)


@dataclass
class Box(Generic[T]):
    item: T


class Pair(NamedTuple):
    a: int
    b: int


class Options(TypedDict):
    name: str


@dataclass
class Node:
    child: "Node | None" = None


@dataclass
class BrokenOptions:
    value: int = serialized_field(default=0, metadata={"simplibs.serialize": {"alais": "x"}})


def _positive(value) -> bool:
    return value > 0


# ---------- every supported annotation, good data ----------

@pytest.mark.parametrize(
    "annotation, data, expected",
    [
        pytest.param(int, 5, 5, id="int"),
        pytest.param(str, "a", "a", id="str"),
        pytest.param(float, 1, 1.0, id="float_from_int"),
        pytest.param(bool, True, True, id="bool"),
        pytest.param(type(None), None, None, id="none"),
        pytest.param(Any, {"a": [1]}, {"a": [1]}, id="Any"),
        pytest.param(list[int], [1, 2], [1, 2], id="list"),
        pytest.param(set[int], [1, 1], {1}, id="set"),
        pytest.param(frozenset[int], [1, 1], frozenset({1}), id="frozenset"),
        pytest.param(deque[int], [1, 2], deque([1, 2]), id="deque"),
        pytest.param(tuple[int, str], [1, "a"], (1, "a"), id="positional_tuple"),
        pytest.param(tuple[int, ...], [1, 2, 3], (1, 2, 3), id="homogeneous_tuple"),
        pytest.param(dict[str, int], {"a": 1}, {"a": 1}, id="dict"),
        pytest.param(OrderedDict[str, int], {"a": 1}, OrderedDict(a=1), id="ordered_dict"),
        pytest.param(Sequence[int], [1], [1], id="Sequence"),
        pytest.param(Mapping[str, int], {"a": 1}, {"a": 1}, id="Mapping"),
        pytest.param(Set[int], [1], frozenset({1}), id="abstract_Set"),
        pytest.param(int | None, None, None, id="optional_none"),
        pytest.param(Optional[int], 5, 5, id="optional_value"),
        pytest.param(int | str, "a", "a", id="union"),
        pytest.param(Annotated[int, _positive], 5, 5, id="Annotated"),
        pytest.param(Literal["a", "b"], "b", "b", id="Literal"),
        pytest.param(UserId, 5, 5, id="NewType"),
        pytest.param(Point, {"x": 1, "y": 2}, Point(1, 2), id="dataclass"),
        pytest.param(Box[int], {"item": 1}, Box(1), id="generic_dataclass"),
        pytest.param(Pair, {"a": 1, "b": 2}, Pair(1, 2), id="NamedTuple"),
        pytest.param(Options, {"name": "ann"}, {"name": "ann"}, id="TypedDict"),
        pytest.param(Color, "red", Color.RED, id="enum"),
        pytest.param(Level, 1, Level.LOW, id="int_enum"),
        pytest.param(date, "2026-01-02", date(2026, 1, 2), id="date"),
        pytest.param(datetime, "2026-01-02T03:04:05", datetime(2026, 1, 2, 3, 4, 5), id="datetime"),
        pytest.param(time, "03:04:05", time(3, 4, 5), id="time"),
        pytest.param(timedelta, 90, timedelta(seconds=90), id="timedelta"),
        pytest.param(PurePosixPath, "a/b", PurePosixPath("a/b"), id="path"),
        pytest.param(UUID, "00000000-0000-0000-0000-000000000001", UUID(int=1), id="uuid"),
        pytest.param(Decimal, "1.10", Decimal("1.10"), id="decimal"),
        pytest.param(Fraction, "1/3", Fraction(1, 3), id="fraction"),
        pytest.param(bytes, "aGk=", b"hi", id="bytes"),
        pytest.param(IPv4Address, "1.2.3.4", IPv4Address("1.2.3.4"), id="ip_address"),
    ],
)
def test_every_supported_annotation(annotation, data, expected):
    result = deserialize(data, annotation)

    assert result == expected
    assert type(result) is type(expected)


# ---------- every supported annotation, bad data ----------

@pytest.mark.parametrize(
    "annotation, data, error_name, label",
    [
        pytest.param(int, "x", "DESERIALIZE_WRONG_TYPE", "$", id="wrong_primitive"),
        pytest.param(list[int], [1, "x"], "DESERIALIZE_WRONG_TYPE", "$[1]", id="item_of_a_list"),
        pytest.param(dict[str, int], {"a": "x"}, "DESERIALIZE_WRONG_TYPE", "$.a", id="value_of_a_dict"),
        pytest.param(dict[int, str], {"a": "x"}, "DESERIALIZE_INVALID_KEY", "$", id="key_of_a_dict"),
        pytest.param(tuple[int, str], [1], "DESERIALIZE_WRONG_LENGTH", "$", id="length_of_a_tuple"),
        pytest.param(Literal["a"], "b", "DESERIALIZE_LITERAL_MISMATCH", "$", id="literal"),
        pytest.param(int | str, None, "DESERIALIZE_UNION_NO_MATCH", "$", id="union"),
        pytest.param(Annotated[int, _positive], -1, "DESERIALIZE_RULE_FAILED", "$", id="rule"),
        pytest.param(Point, {"x": 1}, "DESERIALIZE_MISSING_FIELD", "$", id="missing_field"),
        pytest.param(Point, {"x": 1, "y": 2, "z": 3}, "DESERIALIZE_UNKNOWN_FIELD", "$", id="unknown_field"),
        pytest.param(Pair, "x", "DESERIALIZE_WRONG_TYPE", "$", id="named_tuple"),
        pytest.param(Options, {}, "DESERIALIZE_MISSING_FIELD", "$", id="typed_dict"),
        pytest.param(Color, "blue", "DESERIALIZE_BUILD_FAILED", "$", id="enum_value"),
        pytest.param(date, "not a date", "DESERIALIZE_BUILD_FAILED", "$", id="date_text"),
        pytest.param(date, None, "DESERIALIZE_WRONG_TYPE", "$", id="none_for_a_class_with_a_handler"),
        pytest.param(Callable[..., int], 1, "DESERIALIZE_UNSUPPORTED_ANNOTATION", "$", id="unsupported"),
    ],
)
def test_every_card_with_its_location(annotation, data, error_name, label):
    with pytest.raises(DeserializationError) as caught:
        deserialize(data, annotation)

    assert caught.value.error_name == error_name
    assert caught.value.label == label


def test_the_location_reaches_through_several_levels():
    data = {"servers": [{"host": "a", "port": 1}, {"host": "b", "port": 2}, {"host": "c", "port": "x"}]}

    with pytest.raises(DeserializationError) as caught:
        deserialize(data, Config)

    assert caught.value.label == "$.servers[2].port"


# ---------- strict ----------

def test_strict_is_on_by_default():
    with pytest.raises(DeserializationError) as caught:
        deserialize({"x": 1, "y": 2, "z": 3}, Point)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"


def test_strict_off_ignores_unknown_keys_at_every_level():
    data = {"servers": [{"host": "a", "port": 1, "extra": True}], "unknown": 1}

    assert deserialize(data, Config, strict=False) == Config([Server("a", 1)])


def test_strict_off_does_not_excuse_a_missing_field():
    with pytest.raises(DeserializationError) as caught:
        deserialize({"x": 1, "zz": 3}, Point, strict=False)

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"


# ---------- the data is left alone ----------

def test_the_data_is_not_changed():
    data = {"servers": [{"host": "a", "port": 1}], "tags": ["b", "a"]}
    before = copy.deepcopy(data)

    deserialize(data, Config)

    assert data == before


def test_containers_are_new_ones_not_the_data_itself():
    data = [1, 2]

    result = deserialize(data, list[int])
    result.append(3)

    assert data == [1, 2]


# ---------- very deep data ----------

# Deeper than the recursion limit of every supported Python (3.12+ counts C recursion separately)
_DEPTH = 100_000


def test_data_nested_beyond_the_interpreters_limit_is_a_data_too_deep_card():
    data: dict = {}
    for _ in range(_DEPTH):
        data = {"child": data}

    with pytest.raises(DeserializationError) as caught:
        deserialize(data, Node)

    assert caught.value.error_name == "DESERIALIZE_DATA_TOO_DEEP"


def test_a_moderately_deep_structure_is_fine():
    data: dict = {}
    for _ in range(20):
        data = {"child": data}

    result = deserialize(data, Node)

    assert isinstance(result, Node)


# ---------- what is not a card ----------

def test_broken_field_options_are_a_param_error_not_a_deserialization_error():
    with pytest.raises(ParamError):
        deserialize({"value": 1}, BrokenOptions)


# ---------- with serialize ----------

def test_round_trip_of_every_supported_kind(subtests):
    assert_round_trip(subtests, 5)
    assert_round_trip(subtests, "text")
    assert_round_trip(subtests, [1, [2, 3]], list[int | list[int]])
    assert_round_trip(subtests, {"a": [1, 2]}, dict[str, list[int]])
    assert_round_trip(subtests, {1: "a", 2: "b"}, dict[int, str])
    assert_round_trip(subtests, {"b", "a"}, set[str])
    assert_round_trip(subtests, (1, "a"), tuple[int, str])
    assert_round_trip(subtests, Config([Server("a", 1)], {"x", "y"}))
    assert_round_trip(subtests, Box(1), Box[int])
    assert_round_trip(subtests, Pair(1, 2))
    assert_round_trip(subtests, {"name": "ann"}, Options)
    assert_round_trip(subtests, Color.RED)
    assert_round_trip(subtests, Level.LOW)
    assert_round_trip(subtests, [date(2026, 1, 2)], list[date])
    assert_round_trip(subtests, datetime(2026, 1, 2, 3, 4, 5))
    assert_round_trip(subtests, timedelta(seconds=90))
    assert_round_trip(subtests, UUID(int=1))
    assert_round_trip(subtests, Decimal("1.10"))
    assert_round_trip(subtests, b"hi")
    assert_round_trip(subtests, None, int | None)
