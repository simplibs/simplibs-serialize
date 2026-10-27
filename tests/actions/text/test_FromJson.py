from dataclasses import dataclass
from typing import Any

import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ValidationError

from simplibs.serialize import DeserializationError
from simplibs.serialize.actions import FromJson, ToJson


@dataclass
class Point:
    x: int
    y: int


def test_from_json_contract(subtests) -> None:
    """Verify the execution and construction contract of the FromJson action."""
    assert_action(
        subtests,
        FromJson(annotation=Point),
        valid_values=['{"x": 1, "y": 2}', b'{"x": 3, "y": 4}'],
        expected_outputs=[Point(1, 2), Point(3, 4)],
        invalid_values=['{"x":', '{"x": "a", "y": 2}', 5],
        expected_exception_type=[DeserializationError, DeserializationError, ValidationError],
        expected_input_type=str | bytes,
        expected_output_type=Any,
        action_class=FromJson,
        invalid_init_params=[
            ((), {"annotation": Point, "strict": "yes"}),
            ((), {"annotation": Point, "strict": 1}),
        ],
        verbose=False,
    )


def test_from_json_requires_an_annotation() -> None:
    with pytest.raises(TypeError):
        FromJson()


def test_from_json_invalid_text_is_an_invalid_json_card_with_the_position() -> None:
    with pytest.raises(DeserializationError) as caught:
        FromJson(annotation=Point)('{\n  "x": 1\n  "y": 2\n}')

    assert caught.value.error_name == "DESERIALIZE_INVALID_JSON"
    assert "line 3, column 3" in str(caught.value.problem)


def test_from_json_is_strict_by_default() -> None:
    with pytest.raises(DeserializationError) as caught:
        FromJson(annotation=Point)('{"x": 1, "y": 2, "z": 3}')

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"


def test_from_json_not_strict_ignores_unknown_keys() -> None:
    assert FromJson(annotation=Point, strict=False)('{"x": 1, "y": 2, "z": 3}') == Point(1, 2)


def test_from_json_builds_the_configured_annotation() -> None:
    assert FromJson(annotation=list[int])("[1, 2]") == [1, 2]


def test_to_json_then_from_json_gives_the_object_back() -> None:
    pipeline = ToJson(indent=None) >> FromJson(annotation=list[Point])

    assert pipeline([Point(1, 2)]) == [Point(1, 2)]
