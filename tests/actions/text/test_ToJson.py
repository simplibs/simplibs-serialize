from dataclasses import dataclass
from typing import Any

import pytest
from simplibs.actions.testing import assert_action

from simplibs.serialize import SerializationError
from simplibs.serialize.actions import FromJson, ToJson


@dataclass
class Point:
    x: int
    y: int


class Unknown:
    """Nothing knows this class."""


def test_to_json_contract(subtests) -> None:
    """Verify the execution and construction contract of the ToJson action."""
    assert_action(
        subtests,
        ToJson(indent=None),
        valid_values=[Point(1, 2), {"a": [1, 2]}, "č"],
        expected_outputs=['{"x": 1, "y": 2}', '{"a": [1, 2]}', '"č"'],
        invalid_values=[Unknown(), [float("nan")]],
        expected_exception_type=SerializationError,
        expected_input_type=Any,
        expected_output_type=str,
        action_class=ToJson,
        invalid_init_params=[
            ((), {"indent": []}),
            ((), {"sort_keys": "yes"}),
            ((), {"default": 5}),
        ],
        verbose=False,
    )


def test_to_json_is_indented_by_default() -> None:
    assert ToJson()(Point(1, 2)) == '{\n  "x": 1,\n  "y": 2\n}'


def test_to_json_sort_keys() -> None:
    assert ToJson(indent=None, sort_keys=True)({"b": 1, "a": 2}) == '{"a": 2, "b": 1}'


def test_to_json_ensure_ascii() -> None:
    assert ToJson(indent=None, ensure_ascii=True)("č") == '"\\u010d"'


def test_to_json_allow_nan() -> None:
    assert ToJson(indent=None, allow_nan=True)(float("nan")) == "NaN"


def test_to_json_default_deals_with_an_unknown_type() -> None:
    assert ToJson(indent=None, default=lambda obj: "unknown")({"a": Unknown()}) == '{"a": "unknown"}'


def test_to_json_has_no_option_the_function_does_not_have() -> None:
    with pytest.raises(TypeError):
        ToJson(trailing_newline=True)


def test_to_json_then_from_json_gives_the_object_back() -> None:
    pipeline = ToJson() >> FromJson(annotation=Point)

    assert pipeline(Point(1, 2)) == Point(1, 2)
