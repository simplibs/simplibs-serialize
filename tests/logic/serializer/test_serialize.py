import json
from collections import OrderedDict, deque, namedtuple
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, IntEnum
from fractions import Fraction
from ipaddress import IPv4Address
from pathlib import PurePosixPath
from typing import NamedTuple
from uuid import UUID

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import SerializationError, register_type, serialize, serialized_field
from simplibs.serialize.testing import assert_round_trip


class Color(Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


class TypedPoint(NamedTuple):
    x: int
    y: int


CollectionsPoint = namedtuple("CollectionsPoint", ["x", "y"])


@dataclass
class Inner:
    value: int


@dataclass
class Record:
    name: str
    inner: Inner
    tags: set[str]
    when: datetime


@dataclass
class BrokenOptions:
    value: int = serialized_field(default=0, metadata={"simplibs.serialize": {"alais": "x"}})


class Unknown:
    """Nothing knows this class."""


def _assert_json_only(value):
    """Walk the result and fail on anything `json.dumps` would not write as it is."""
    if value is None or type(value) in (bool, int, float, str):
        return
    if type(value) is list:
        for item in value:
            _assert_json_only(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            assert type(key) is str
            _assert_json_only(item)
        return
    raise AssertionError(f"not a JSON value: {value!r}")


# ---------- every supported kind once ----------

@pytest.mark.parametrize(
    "obj, expected",
    [
        pytest.param(None, None, id="none"),
        pytest.param(True, True, id="bool"),
        pytest.param(5, 5, id="int"),
        pytest.param(1.5, 1.5, id="float"),
        pytest.param("text", "text", id="str"),
        pytest.param([1, [2]], [1, [2]], id="list"),
        pytest.param((1, 2), [1, 2], id="tuple"),
        pytest.param(deque([1, 2]), [1, 2], id="deque"),
        pytest.param({3, 1, 2}, [1, 2, 3], id="set"),
        pytest.param(frozenset({"b", "a"}), ["a", "b"], id="frozenset"),
        pytest.param({"a": {"b": 1}}, {"a": {"b": 1}}, id="dict"),
        pytest.param(OrderedDict(a=1), {"a": 1}, id="ordered_dict"),
        pytest.param({1: "a", None: "b", 1.5: "c"}, {"1": "a", "null": "b", "1.5": "c"}, id="keys_as_text"),
        pytest.param(Inner(1), {"value": 1}, id="dataclass"),
        pytest.param(TypedPoint(1, 2), {"x": 1, "y": 2}, id="NamedTuple"),
        pytest.param(CollectionsPoint(1, 2), {"x": 1, "y": 2}, id="namedtuple"),
        pytest.param(Color.RED, "red", id="enum"),
        pytest.param(Level.LOW, 1, id="int_enum"),
        pytest.param(datetime(2026, 1, 2, 3, 4, 5), "2026-01-02T03:04:05", id="datetime"),
        pytest.param(date(2026, 1, 2), "2026-01-02", id="date"),
        pytest.param(time(3, 4, 5), "03:04:05", id="time"),
        pytest.param(timedelta(seconds=90), 90.0, id="timedelta"),
        pytest.param(PurePosixPath("a/b"), "a/b", id="path"),
        pytest.param(UUID(int=1), "00000000-0000-0000-0000-000000000001", id="uuid"),
        pytest.param(Decimal("1.10"), "1.10", id="decimal"),
        pytest.param(Fraction(1, 3), "1/3", id="fraction"),
        pytest.param(b"hi", "aGk=", id="bytes"),
        pytest.param(IPv4Address("1.2.3.4"), "1.2.3.4", id="ip_address"),
    ],
)
def test_every_supported_kind(obj, expected):
    result = serialize(obj)

    assert result == expected
    _assert_json_only(result)
    json.dumps(result, allow_nan=False)


def test_a_nested_structure_of_many_kinds():
    obj = {"when": date(2026, 1, 2), "items": [Inner(1), (Color.RED, {2, 1})], "id": UUID(int=1)}

    assert serialize(obj) == {
        "when": "2026-01-02",
        "items": [{"value": 1}, ["red", [1, 2]]],
        "id": "00000000-0000-0000-0000-000000000001",
    }


# ---------- sets in a fixed order ----------

def test_a_set_always_gives_the_same_list():
    results = {json.dumps(serialize({"b", "a", "c", "d", "e"})) for _ in range(5)}

    assert results == {'["a", "b", "c", "d", "e"]'}


def test_sets_built_in_different_order_give_the_same_list():
    assert serialize(set(["x", "y", "z"])) == serialize(set(["z", "y", "x"])) == ["x", "y", "z"]


# ---------- nan ----------

def test_a_nan_is_an_error_by_default():
    with pytest.raises(SerializationError) as caught:
        serialize({"price": float("nan")})

    assert caught.value.error_name == "SERIALIZE_NON_FINITE_NUMBER"
    assert caught.value.label == "$.price"


def test_a_nan_passes_when_it_is_allowed():
    result = serialize([float("inf"), 1.0], allow_nan=True)

    assert result == [float("inf"), 1.0]


# ---------- every card with its location ----------

def test_an_unsupported_type_names_the_place():
    with pytest.raises(SerializationError) as caught:
        serialize({"items": [1, Unknown()]})

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_TYPE"
    assert caught.value.label == "$.items[1]"


def test_a_circular_reference_names_the_place():
    data = {"rows": []}
    data["rows"].append(data)

    with pytest.raises(SerializationError) as caught:
        serialize(data)

    assert caught.value.error_name == "SERIALIZE_CIRCULAR_REFERENCE"
    assert caught.value.label == "$.rows[0]"


def test_two_keys_with_one_text_name_the_place():
    with pytest.raises(SerializationError) as caught:
        serialize({"table": {1: "a", "1": "b"}})

    assert caught.value.error_name == "SERIALIZE_DUPLICATE_KEY"
    assert caught.value.label == "$.table"


def test_a_key_that_cannot_be_text_names_the_place():
    with pytest.raises(SerializationError) as caught:
        serialize({"table": {(1, 2): "a"}})

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_KEY"
    assert caught.value.label == "$.table"


def test_a_failing_handler_names_the_place_and_keeps_the_cause():
    failure = ZeroDivisionError("division by zero")

    def failing(obj):
        raise failure

    register_type(Unknown, to_func=failing)

    with pytest.raises(SerializationError) as caught:
        serialize([Unknown()])

    assert caught.value.error_name == "SERIALIZE_HANDLER_FAILED"
    assert caught.value.label == "$[0]"
    assert caught.value.__cause__ is failure


# ---------- default= ----------

def test_default_is_used_for_an_unknown_type():
    assert serialize([Unknown()], default=lambda obj: "unknown") == ["unknown"]


def test_default_is_not_used_for_what_the_library_knows():
    def never(obj):
        raise AssertionError("called")

    assert serialize({"a": [date(2026, 1, 2), Color.RED]}, default=never) == {"a": ["2026-01-02", "red"]}


def test_default_that_keeps_returning_new_unknown_objects_ends_in_a_card():
    with pytest.raises(SerializationError) as caught:
        serialize(Unknown(), default=lambda obj: Unknown())

    assert caught.value.error_name == "SERIALIZE_TOO_DEEP"


def test_default_that_returns_its_own_argument_is_a_circle():
    with pytest.raises(SerializationError) as caught:
        serialize(Unknown(), default=lambda obj: obj)

    assert caught.value.error_name == "SERIALIZE_CIRCULAR_REFERENCE"


# ---------- very deep data ----------

# Deeper than the recursion limit of every supported Python (3.12+ counts C recursion separately)
_DEPTH = 100_000


def test_a_very_deep_structure_gives_the_too_deep_card():
    data: list = []
    for _ in range(_DEPTH):
        data = [data]

    with pytest.raises(SerializationError) as caught:
        serialize(data)

    assert caught.value.error_name == "SERIALIZE_TOO_DEEP"


# ---------- what passes through ----------

def test_broken_field_options_are_a_param_error_not_a_serialization_error():
    with pytest.raises(ParamError):
        serialize(BrokenOptions())


def test_the_result_is_new_data_not_the_input():
    original = {"a": [1, 2]}

    result = serialize(original)
    result["a"].append(3)

    assert original == {"a": [1, 2]}


# ---------- with deserialize ----------

def test_round_trip_of_a_rich_record(subtests):
    record = Record("ann", Inner(1), {"b", "a"}, datetime(2026, 1, 2, 3, 4, 5))

    assert_round_trip(subtests, record)


def test_round_trip_of_containers_and_enums(subtests):
    assert_round_trip(subtests, [Color.RED, Color.RED], list[Color])
    assert_round_trip(subtests, {"a": Level.LOW}, dict[str, Level])
    assert_round_trip(subtests, {1: "a", 2: "b"}, dict[int, str])
