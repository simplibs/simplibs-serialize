from dataclasses import dataclass
from typing import Any

import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ValidationError

from simplibs.serialize import DeserializationError
from simplibs.serialize.actions import Deserialize, Serialize


@dataclass
class Point:
    x: int
    y: int


def test_deserialize_contract(subtests) -> None:
    """Verify the execution and construction contract of the Deserialize action."""
    assert_action(
        subtests,
        Deserialize(annotation=Point),
        valid_values=[{"x": 1, "y": 2}, {"x": 3, "y": 4}],
        expected_outputs=[Point(1, 2), Point(3, 4)],
        invalid_values=[{"x": "a", "y": 2}, {"x": 1}, [1]],
        expected_exception_type=DeserializationError,
        expected_input_type=Any,
        expected_output_type=Any,
        action_class=Deserialize,
        invalid_init_params=[
            ((), {"annotation": Point, "strict": "yes"}),
            ((), {"annotation": Point, "strict": 1}),
        ],
        verbose=False,
    )


def test_deserialize_requires_an_annotation() -> None:
    with pytest.raises(TypeError):
        Deserialize()


def test_deserialize_is_strict_by_default() -> None:
    with pytest.raises(DeserializationError) as caught:
        Deserialize(annotation=Point)({"x": 1, "y": 2, "z": 3})

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"


def test_deserialize_not_strict_ignores_unknown_keys() -> None:
    assert Deserialize(annotation=Point, strict=False)({"x": 1, "y": 2, "z": 3}) == Point(1, 2)


def test_deserialize_builds_the_configured_annotation_not_a_guessed_one() -> None:
    assert Deserialize(annotation=list[Point])([{"x": 1, "y": 2}]) == [Point(1, 2)]
    assert Deserialize(annotation=dict[str, int])({"a": 1}) == {"a": 1}


def test_one_action_builds_one_annotation_for_every_call() -> None:
    action = Deserialize(annotation=Point)

    assert action({"x": 1, "y": 2}) == Point(1, 2)
    assert action({"x": 3, "y": 4}) == Point(3, 4)


def test_serialize_then_deserialize_gives_the_object_back() -> None:
    pipeline = Serialize() >> Deserialize(annotation=list[Point])

    assert pipeline([Point(1, 2), Point(3, 4)]) == [Point(1, 2), Point(3, 4)]
