from collections import ChainMap, OrderedDict, defaultdict
from types import MappingProxyType

import pytest

from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_mapping, encode_value


def _context(convert=lambda obj: obj):
    """A context whose dispatcher only records the calls and applies `convert`."""
    calls = []

    def fake_encode_value(obj, location, context):
        calls.append((obj, location))
        return convert(obj)

    return SerializeContext(default=None, allow_nan=False, encode_value=fake_encode_value), calls


@pytest.mark.parametrize(
    "obj",
    [
        pytest.param({"a": 1, "b": 2}, id="dict"),
        pytest.param(OrderedDict(a=1, b=2), id="ordered_dict"),
        pytest.param(defaultdict(int, a=1, b=2), id="defaultdict"),
        pytest.param(MappingProxyType({"a": 1, "b": 2}), id="mapping_proxy"),
        pytest.param(ChainMap({"a": 1}, {"b": 2}), id="chain_map"),
    ],
)
def test_any_mapping_gives_a_plain_dict(obj):
    context, _ = _context()

    result = encode_mapping(obj, (), context)

    assert result == {"a": 1, "b": 2}
    assert type(result) is dict


def test_insertion_order_is_kept():
    context, _ = _context()

    assert list(encode_mapping({"b": 1, "a": 2, "c": 3}, (), context)) == ["b", "a", "c"]


def test_keys_become_text_and_values_are_converted_below_them():
    context, calls = _context(convert=lambda obj: obj.upper() if isinstance(obj, str) else obj)

    result = encode_mapping({1: "a", "x": "b"}, ("data",), context)

    assert result == {"1": "A", "x": "B"}
    assert ("a", ("data", "1")) in calls
    assert ("b", ("data", "x")) in calls


def test_a_key_with_a_dot_stays_one_step_of_the_location():
    context, calls = _context()

    encode_mapping({"a.b": 1}, (), context)

    assert calls == [(1, ("a.b",))]


def test_the_location_of_a_failing_value_names_the_key():
    context = SerializeContext(default=None, allow_nan=False, encode_value=encode_value)

    with pytest.raises(SerializationError) as caught:
        encode_mapping({"a.b": object()}, (), context)

    assert caught.value.label == "$['a.b']"


def test_two_keys_with_one_text_are_an_error():
    context, _ = _context()

    with pytest.raises(SerializationError) as caught:
        encode_mapping({1: "a", "1": "b"}, ("table",), context)

    assert caught.value.error_name == "SERIALIZE_DUPLICATE_KEY"
    assert caught.value.label == "$.table"
    assert caught.value.value == "1"


def test_a_key_that_cannot_be_text_is_an_error():
    context, _ = _context()

    with pytest.raises(SerializationError) as caught:
        encode_mapping({(1, 2): "a"}, (), context)

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_KEY"
