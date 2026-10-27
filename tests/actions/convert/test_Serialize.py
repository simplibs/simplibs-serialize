from dataclasses import dataclass
from datetime import date
from typing import Any

import pytest
from simplibs.actions.testing import assert_action

from simplibs.serialize import SerializationError
from simplibs.serialize.actions import Deserialize, Serialize


@dataclass
class Point:
    x: int
    y: int


class Unknown:
    """Nothing knows this class."""


def test_serialize_contract(subtests) -> None:
    """Verify the execution and construction contract of the Serialize action."""
    assert_action(
        subtests,
        Serialize(),
        valid_values=[Point(1, 2), {"tags": {"b", "a"}}, date(2026, 1, 2), None],
        expected_outputs=[{"x": 1, "y": 2}, {"tags": ["a", "b"]}, "2026-01-02", None],
        invalid_values=[Unknown(), {"price": float("nan")}],
        expected_exception_type=SerializationError,
        expected_input_type=Any,
        action_class=Serialize,
        invalid_init_params=[((), {"default": 5}), ((), {"allow_nan": "yes"})],
        verbose=False,
    )


def test_serialize_default_deals_with_an_unknown_type() -> None:
    assert Serialize(default=lambda obj: "unknown")([Unknown()]) == ["unknown"]


def test_serialize_allow_nan_lets_a_non_finite_number_through() -> None:
    assert Serialize(allow_nan=True)([float("inf"), 1.0]) == [float("inf"), 1.0]


def test_serialize_has_no_option_the_function_does_not_have() -> None:
    with pytest.raises(TypeError):
        Serialize(indent=2)


def test_serialize_then_deserialize_gives_the_object_back() -> None:
    pipeline = Serialize() >> Deserialize(annotation=Point)

    assert pipeline(Point(1, 2)) == Point(1, 2)
