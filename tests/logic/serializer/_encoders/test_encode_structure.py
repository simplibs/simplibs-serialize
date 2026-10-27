import math
from collections import ChainMap, OrderedDict, deque, namedtuple
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, IntEnum
from types import MappingProxyType
from typing import NamedTuple

import pytest

from simplibs.serialize import SerializationError, register_type
from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_structure, encode_value


class Color(str, Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


class Name(str):
    """A str subclass."""


class Port(int):
    """An int subclass."""


class Ratio(float):
    """A float subclass."""


class TypedPoint(NamedTuple):
    x: int
    y: int


CollectionsPoint = namedtuple("CollectionsPoint", ["x", "y"])


class MyDict(dict):
    """A dict subclass."""


class Unknown:
    """Nothing knows this class."""


@dataclass
class Record:
    a: int


def _context(default=None) -> SerializeContext:
    return SerializeContext(default=default, allow_nan=False, encode_value=encode_value)


def _never_called(obj):
    raise AssertionError("default was called for something that is known")


# ---------- 1. a handler first ----------

def test_a_builtin_handler_is_used():
    assert encode_structure(datetime(2026, 1, 2, 3, 4, 5), (), _context()) == "2026-01-02T03:04:05"


def test_bytes_are_text_not_a_list():
    assert encode_structure(b"hi", (), _context()) == "aGk="


def test_a_registered_handler_wins_over_the_rule_for_the_base_class():
    register_type(MyDict, to_func=lambda obj: {"handled": True})

    assert encode_structure(MyDict(a=1), (), _context()) == {"handled": True}


# ---------- 2. subclasses of str, int, float ----------

@pytest.mark.parametrize(
    "obj, expected, kind",
    [
        pytest.param(Name("abc"), "abc", str, id="str_subclass"),
        pytest.param(Port(8080), 8080, int, id="int_subclass"),
        pytest.param(Ratio(1.5), 1.5, float, id="float_subclass"),
    ],
)
def test_a_subclass_of_a_primitive_gives_the_plain_value(obj, expected, kind):
    result = encode_structure(obj, (), _context())

    assert result == expected
    assert type(result) is kind


@pytest.mark.parametrize(
    "member, expected",
    [pytest.param(Color.RED, "red", id="str_enum"), pytest.param(Level.LOW, 1, id="int_enum")],
)
def test_an_enum_gives_its_value_not_its_name(member, expected):
    result = encode_structure(member, (), _context())

    assert result == expected
    assert type(result) is type(expected)


# ---------- 3. NamedTuple ----------

@pytest.mark.parametrize("obj", [TypedPoint(1, 2), CollectionsPoint(1, 2)], ids=["NamedTuple", "namedtuple"])
def test_a_named_tuple_is_a_dict_of_its_fields(obj):
    assert encode_structure(obj, (), _context()) == {"x": 1, "y": 2}


# ---------- 4. mappings ----------

@pytest.mark.parametrize(
    "obj",
    [MyDict(a=1), OrderedDict(a=1), MappingProxyType({"a": 1}), ChainMap({"a": 1})],
    ids=["dict_subclass", "ordered_dict", "mapping_proxy", "chain_map"],
)
def test_any_mapping_is_a_dict(obj):
    result = encode_structure(obj, (), _context())

    assert result == {"a": 1}
    assert type(result) is dict


# ---------- 5. dataclasses ----------

def test_a_dataclass_instance_is_a_dict():
    assert encode_structure(Record(1), (), _context()) == {"a": 1}


def test_a_dataclass_class_is_not_data():
    with pytest.raises(SerializationError) as caught:
        encode_structure(Record, (), _context())

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_TYPE"


# ---------- 6. sequences and sets ----------

@pytest.mark.parametrize(
    "obj, expected",
    [
        pytest.param([3, 1], [3, 1], id="list"),
        pytest.param((3, 1), [3, 1], id="tuple"),
        pytest.param(deque([3, 1]), [3, 1], id="deque"),
        pytest.param(range(2), [0, 1], id="range"),
        pytest.param({3, 1}, [1, 3], id="set"),
        pytest.param(frozenset({3, 1}), [1, 3], id="frozenset"),
        pytest.param({"b": 1, "a": 2}.keys(), ["a", "b"], id="dict_keys"),
        pytest.param({"b": 1, "a": 2}.values(), [1, 2], id="dict_values"),
    ],
)
def test_a_sequence_a_set_or_a_view_is_a_list(obj, expected):
    assert encode_structure(obj, (), _context()) == expected


# ---------- 7. the caller's default ----------

def test_default_is_used_for_an_object_nothing_else_knows():
    result = encode_structure(Unknown(), (), _context(default=lambda obj: {"unknown": True}))

    assert result == {"unknown": True}


def test_the_result_of_default_is_converted_again():
    result = encode_structure(Unknown(), (), _context(default=lambda obj: {"when": date(2026, 1, 2)}))

    assert result == {"when": "2026-01-02"}


@pytest.mark.parametrize(
    "obj",
    [datetime(2026, 1, 2), Name("a"), TypedPoint(1, 2), {"a": 1}, Record(1), [1], Color.RED, b"x"],
    ids=["handler", "str_subclass", "named_tuple", "mapping", "dataclass", "sequence", "enum", "bytes"],
)
def test_default_never_overrides_a_rule_the_library_has(obj):
    encode_structure(obj, (), _context(default=_never_called))


# ---------- 8. nothing recognized ----------

@pytest.mark.parametrize("obj", [Unknown(), object(), 1 + 2j], ids=["custom_class", "object", "complex"])
def test_an_unknown_object_is_an_error(obj):
    with pytest.raises(SerializationError) as caught:
        encode_structure(obj, ("items", 1), _context())

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_TYPE"
    assert caught.value.label == "$.items[1]"
    assert caught.value.value is obj


def test_the_defaults_failure_is_a_handler_card():
    def failing(obj):
        raise KeyError("missing")

    with pytest.raises(SerializationError) as caught:
        encode_structure(Unknown(), (), _context(default=failing))

    assert caught.value.error_name == "SERIALIZE_HANDLER_FAILED"
