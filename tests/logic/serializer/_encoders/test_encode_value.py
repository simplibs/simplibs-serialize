import math
from dataclasses import dataclass

import pytest

from simplibs.serialize import SerializationError, register_type
from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_value


class Point:
    """A custom class used with a handler."""


class Ratio(float):
    """A float subclass."""


def _context(allow_nan=False) -> SerializeContext:
    return SerializeContext(default=None, allow_nan=allow_nan, encode_value=encode_value)


@pytest.mark.parametrize(
    "obj",
    [None, "text", "", 0, 5, -1, 1.5, True, False],
    ids=["none", "text", "empty_text", "zero", "int", "negative_int", "float", "true", "false"],
)
def test_a_primitive_passes_through_unchanged(obj):
    result = encode_value(obj, (), _context())

    assert result == obj
    assert type(result) is type(obj)


def test_a_primitive_never_enters_the_path():
    context = _context()

    encode_value("text", (), context)
    encode_value(5, (), context)

    assert context.ancestors == set()


# ---------- nan and inf ----------

@pytest.mark.parametrize("number", [float("nan"), float("inf"), float("-inf")], ids=["nan", "inf", "minus_inf"])
def test_a_non_finite_number_is_an_error_by_default(number):
    with pytest.raises(SerializationError) as caught:
        encode_value(number, ("price",), _context())

    assert caught.value.error_name == "SERIALIZE_NON_FINITE_NUMBER"
    assert caught.value.label == "$.price"


@pytest.mark.parametrize("number", [float("nan"), float("inf"), float("-inf")], ids=["nan", "inf", "minus_inf"])
def test_a_non_finite_number_passes_when_it_is_allowed(number):
    result = encode_value(number, (), _context(allow_nan=True))

    assert repr(result) == repr(number)


def test_a_non_finite_float_subclass_is_an_error_too():
    with pytest.raises(SerializationError) as caught:
        encode_value(Ratio("nan"), (), _context())

    assert caught.value.error_name == "SERIALIZE_NON_FINITE_NUMBER"


# ---------- circles ----------

def test_a_list_that_contains_itself_is_a_circle():
    data: list = []
    data.append(data)

    with pytest.raises(SerializationError) as caught:
        encode_value(data, (), _context())

    assert caught.value.error_name == "SERIALIZE_CIRCULAR_REFERENCE"
    assert caught.value.label == "$[0]"


def test_a_dict_that_contains_itself_is_a_circle():
    data: dict = {}
    data["me"] = data

    with pytest.raises(SerializationError) as caught:
        encode_value(data, (), _context())

    assert caught.value.error_name == "SERIALIZE_CIRCULAR_REFERENCE"
    assert caught.value.label == "$.me"


def test_a_dataclass_that_reaches_itself_is_a_circle():
    @dataclass
    class Node:
        child: object = None

    node = Node()
    node.child = node

    with pytest.raises(SerializationError) as caught:
        encode_value(node, (), _context())

    assert caught.value.error_name == "SERIALIZE_CIRCULAR_REFERENCE"


def test_a_handler_that_returns_its_own_argument_is_a_circle():
    register_type(Point, to_func=lambda point: point)

    with pytest.raises(SerializationError) as caught:
        encode_value(Point(), (), _context())

    assert caught.value.error_name == "SERIALIZE_CIRCULAR_REFERENCE"


def test_the_same_list_twice_side_by_side_is_not_a_circle():
    shared = [1, 2]

    assert encode_value([shared, shared], (), _context()) == [[1, 2], [1, 2]]


def test_the_path_is_clean_after_success():
    context = _context()

    encode_value({"a": [1, {"b": 2}]}, (), context)

    assert context.ancestors == set()


def test_the_path_is_clean_after_an_error():
    context = _context()

    with pytest.raises(SerializationError):
        encode_value({"a": [1, object()]}, (), context)

    assert context.ancestors == set()


def test_a_value_is_converted_through_the_structure_path():
    assert encode_value({"a": (1, 2)}, (), _context()) == {"a": [1, 2]}
