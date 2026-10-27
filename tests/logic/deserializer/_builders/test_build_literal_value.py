from enum import Enum, IntEnum
from typing import Literal

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_literal_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class Level(IntEnum):
    LOW = 1


class Name(str, Enum):
    ANN = "ann"


def _context() -> DeserializeContext:
    return DeserializeContext(strict=True, build_value=build_value)


@pytest.mark.parametrize(
    "annotation, data",
    [
        pytest.param(Literal["debug", "info"], "info", id="text"),
        pytest.param(Literal[1, 2, 3], 2, id="int"),
        pytest.param(Literal[True], True, id="true"),
        pytest.param(Literal[False], False, id="false"),
        pytest.param(Literal[None], None, id="none"),
        pytest.param(Literal[1.5], 1.5, id="float"),
        pytest.param(Literal["a", 1, None], 1, id="mixed_int"),
        pytest.param(Literal["a", 1, None], None, id="mixed_none"),
    ],
)
def test_a_listed_value_is_returned(annotation, data):
    result = build_literal_value(data, annotation, (), _context())

    assert result == data
    assert type(result) is type(data)


@pytest.mark.parametrize(
    "annotation, data, member",
    [
        pytest.param(Literal[Color.RED], "red", Color.RED, id="text_enum"),
        pytest.param(Literal[Color.RED, Color.BLUE], "blue", Color.BLUE, id="second_member"),
        pytest.param(Literal[Level.LOW], 1, Level.LOW, id="int_enum"),
        pytest.param(Literal[Name.ANN], "ann", Name.ANN, id="str_enum"),
    ],
)
def test_an_enum_member_is_matched_by_its_value_and_returned_as_the_member(annotation, data, member):
    assert build_literal_value(data, annotation, (), _context()) is member


@pytest.mark.parametrize(
    "annotation, data",
    [
        pytest.param(Literal["debug", "info"], "warning", id="not_listed"),
        pytest.param(Literal["debug"], "DEBUG", id="other_case"),
        pytest.param(Literal[1], True, id="true_is_not_one"),
        pytest.param(Literal[True], 1, id="one_is_not_true"),
        pytest.param(Literal[0], False, id="false_is_not_zero"),
        pytest.param(Literal[1], 1.0, id="float_is_not_int"),
        pytest.param(Literal[1.0], 1, id="int_is_not_float"),
        pytest.param(Literal["1"], 1, id="int_is_not_text"),
        pytest.param(Literal[None], 0, id="zero_is_not_none"),
        pytest.param(Literal[Color.RED], "green", id="enum_value_not_listed"),
        pytest.param(Literal[Color.RED], Color.RED, id="the_member_itself_is_not_data"),
    ],
)
def test_anything_else_is_a_literal_mismatch_card(annotation, data):
    with pytest.raises(DeserializationError) as caught:
        build_literal_value(data, annotation, ("mode",), _context())

    assert caught.value.error_name == "DESERIALIZE_LITERAL_MISMATCH"
    assert caught.value.label == "$.mode"
    assert caught.value.value == data
