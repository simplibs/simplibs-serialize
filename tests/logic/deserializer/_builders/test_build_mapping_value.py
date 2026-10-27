import uuid
from collections import OrderedDict
from collections.abc import Mapping, MutableMapping
from datetime import date
from enum import Enum
from types import MappingProxyType
from typing import Any

import pytest

from simplibs.serialize import DeserializationError, register_type
from simplibs.serialize.logic.deserializer._builders import build_mapping_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class Bucket:
    """A key type whose handler builds something unhashable."""


def _real_context() -> DeserializeContext:
    return DeserializeContext(strict=True, build_value=build_value)


def _fake_context():
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_build_value(data, annotation, location, context):
        calls.append((data, annotation, location))
        return data

    return DeserializeContext(strict=True, build_value=fake_build_value), calls


def _build(data, annotation, location=()):
    return build_mapping_value(data, annotation, location, _real_context())


# ---------- the mapping that is built ----------

@pytest.mark.parametrize(
    "data, annotation, expected",
    [
        pytest.param({"a": 1, "b": 2}, dict[str, int], {"a": 1, "b": 2}, id="str_keys"),
        pytest.param({"1": "a", "2": "b"}, dict[int, str], {1: "a", 2: "b"}, id="int_keys"),
        pytest.param({"1.5": 1}, dict[float, int], {1.5: 1}, id="float_keys"),
        pytest.param({"true": 1, "false": 2}, dict[bool, int], {True: 1, False: 2}, id="bool_keys"),
        pytest.param({"red": 1}, dict[Color, int], {Color.RED: 1}, id="enum_keys"),
        pytest.param({"2026-01-02": 1}, dict[date, int], {date(2026, 1, 2): 1}, id="date_keys"),
        pytest.param(
            {"00000000-0000-0000-0000-000000000001": 1},
            dict[uuid.UUID, int],
            {uuid.UUID(int=1): 1},
            id="uuid_keys",
        ),
        pytest.param({"a": {"b": [1]}}, dict[str, dict[str, list[int]]], {"a": {"b": [1]}}, id="nested_values"),
        pytest.param({"a": 1, "b": "x"}, dict, {"a": 1, "b": "x"}, id="bare_dict"),
        pytest.param({"a": 1}, dict[str, Any], {"a": 1}, id="any_values"),
        pytest.param({}, dict[str, int], {}, id="empty"),
    ],
)
def test_keys_and_values_are_built(data, annotation, expected):
    result = _build(data, annotation)

    assert result == expected
    assert type(result) is dict


@pytest.mark.parametrize(
    "annotation",
    [Mapping[str, int], MutableMapping[str, int]],
    ids=["Mapping", "MutableMapping"],
)
def test_an_abstract_mapping_is_a_plain_dict(annotation):
    result = _build({"a": 1}, annotation)

    assert result == {"a": 1}
    assert type(result) is dict


def test_an_ordered_dict_keeps_its_type_and_the_order_of_the_data():
    result = _build({"b": 1, "a": 2}, OrderedDict[str, int])

    assert type(result) is OrderedDict
    assert list(result) == ["b", "a"]


def test_the_order_of_the_data_is_kept_in_a_dict():
    assert list(_build({"b": 1, "a": 2, "c": 3}, dict[str, int])) == ["b", "a", "c"]


def test_a_mapping_that_is_not_a_dict_is_accepted_as_data():
    assert _build(MappingProxyType({"a": 1}), dict[str, int]) == {"a": 1}


def test_a_key_that_came_from_python_data_is_accepted():
    assert _build({1: "a"}, dict[int, str]) == {1: "a"}


# ---------- data that is no object ----------

@pytest.mark.parametrize(
    "data",
    [[1], "abc", 5, None, True],
    ids=["list", "text", "int", "none", "bool"],
)
def test_data_that_is_not_an_object_is_a_wrong_type_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, dict[str, int], ("table",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.table"
    assert caught.value.value == data


# ---------- locations ----------

def test_a_value_that_does_not_fit_is_located_by_its_key():
    with pytest.raises(DeserializationError) as caught:
        _build({"limits": {"max": "x"}}, dict[str, dict[str, int]])

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.limits.max"


def test_the_location_of_a_value_below_a_key_that_is_not_text_is_the_key_shown_as_text():
    context, calls = _fake_context()

    build_mapping_value({1: "a"}, dict[int, str], ("table",), context)

    assert ("a", str, ("table", "1")) in calls


def test_every_value_is_built_against_the_value_annotation():
    context, calls = _fake_context()

    build_mapping_value({"a": 1, "b": 2}, dict[str, int], ("rows", 0), context)

    assert calls == [(1, int, ("rows", 0, "a")), (2, int, ("rows", 0, "b"))]


# ---------- keys that cannot be told apart or kept ----------

def test_two_texts_that_become_one_key_are_a_key_collision_card():
    with pytest.raises(DeserializationError) as caught:
        _build({"1": 1, "1.0": 2}, dict[float, int], ("table",))

    assert caught.value.error_name == "DESERIALIZE_KEY_COLLISION"
    assert caught.value.label == "$.table"
    assert caught.value.value == "1.0"


def test_a_key_that_cannot_be_read_is_an_invalid_key_card():
    with pytest.raises(DeserializationError) as caught:
        _build({"abc": 1}, dict[int, int], ("table",))

    assert caught.value.error_name == "DESERIALIZE_INVALID_KEY"
    assert caught.value.label == "$.table"


def test_a_key_that_is_built_unhashable_is_a_build_failed_card():
    register_type(Bucket, from_func=lambda data, annotation: [data])

    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1}, dict[Bucket, int], ("table",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.table"
    assert isinstance(caught.value.__cause__, TypeError)
