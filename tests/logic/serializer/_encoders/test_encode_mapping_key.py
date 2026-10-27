import uuid
from datetime import date
from enum import Enum, IntEnum

import pytest
from simplibs.exception import SimpleException

from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_mapping_key, encode_value


class Color(Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


class Name(str):
    """A str subclass."""


def _real_context(allow_nan=False) -> SerializeContext:
    return SerializeContext(default=None, allow_nan=allow_nan, encode_value=encode_value)


def test_a_text_key_is_returned_without_asking_the_dispatcher():
    calls = []

    def fake_encode_value(obj, location, context):
        calls.append(obj)
        return obj

    context = SerializeContext(default=None, allow_nan=False, encode_value=fake_encode_value)

    assert encode_mapping_key("name", (), context) == "name"
    assert calls == []


@pytest.mark.parametrize(
    "key, expected",
    [
        pytest.param(1, "1", id="int"),
        pytest.param(-3, "-3", id="negative_int"),
        pytest.param(1.5, "1.5", id="float"),
        pytest.param(1e100, "1e+100", id="large_float"),
        pytest.param(True, "true", id="true"),
        pytest.param(False, "false", id="false"),
        pytest.param(None, "null", id="none"),
        pytest.param(Name("abc"), "abc", id="str_subclass"),
        pytest.param(Color.RED, "red", id="enum_by_value"),
        pytest.param(Level.LOW, "1", id="int_enum_by_value"),
        pytest.param(date(2026, 1, 2), "2026-01-02", id="date"),
        pytest.param(uuid.UUID(int=1), "00000000-0000-0000-0000-000000000001", id="uuid"),
    ],
)
def test_a_key_becomes_the_text_json_would_write(key, expected):
    assert encode_mapping_key(key, (), _real_context()) == expected


@pytest.mark.parametrize("key", [(1, 2), frozenset({1})], ids=["tuple", "frozenset"])
def test_a_key_that_becomes_a_list_is_unsupported(key):
    with pytest.raises(SerializationError) as caught:
        encode_mapping_key(key, ("table",), _real_context())

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_KEY"
    assert caught.value.label == "$.table"
    assert caught.value.value == key


def test_a_nan_key_is_an_error():
    with pytest.raises(SerializationError) as caught:
        encode_mapping_key(float("nan"), ("table",), _real_context())

    assert caught.value.error_name == "SERIALIZE_NON_FINITE_NUMBER"
    assert caught.value.label == "$.table"


def test_a_nan_key_is_text_when_nan_is_allowed():
    assert encode_mapping_key(float("nan"), (), _real_context(allow_nan=True)) == "nan"
