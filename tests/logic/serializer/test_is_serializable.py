from dataclasses import dataclass
from datetime import date

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import is_serializable, register_type, serialized_field


class Unknown:
    """Nothing knows this class."""


class Registered:
    """A class with a handler."""


@dataclass
class Record:
    name: str
    when: date


@dataclass
class BrokenOptions:
    value: int = serialized_field(default=0, metadata={"simplibs.serialize": {"alais": "x"}})


@pytest.mark.parametrize(
    "obj",
    [
        pytest.param({"a": [1, 2.5, None, True, "x"]}, id="plain_structure"),
        pytest.param(Record("ann", date(2026, 1, 2)), id="dataclass"),
        pytest.param({3, 1, 2}, id="set"),
        pytest.param(5, id="primitive"),
    ],
)
def test_true_for_what_can_be_written(obj):
    assert is_serializable(obj) is True


def test_true_for_a_registered_type():
    register_type(Registered, to_func=lambda obj: "registered")

    assert is_serializable([Registered()]) is True


def test_false_for_an_unknown_type():
    assert is_serializable({"a": Unknown()}) is False


def test_false_for_a_circle():
    data: list = []
    data.append(data)

    assert is_serializable(data) is False


def test_false_for_a_nan():
    assert is_serializable([float("nan")]) is False


def test_false_for_a_dict_with_a_key_that_cannot_be_text():
    assert is_serializable({(1, 2): "a"}) is False


def test_false_for_a_failing_handler():
    register_type(Registered, to_func=lambda obj: 1 / 0)

    assert is_serializable(Registered()) is False


def test_false_for_nesting_that_never_ends():
    assert is_serializable(Unknown(), default=lambda obj: Unknown()) is False


def test_default_makes_an_unknown_type_serializable():
    assert is_serializable({"a": Unknown()}, default=lambda obj: "unknown") is True


def test_allow_nan_makes_a_nan_serializable():
    assert is_serializable([float("nan")], allow_nan=True) is True


def test_a_field_with_broken_options_is_still_a_param_error():
    with pytest.raises(ParamError):
        is_serializable(BrokenOptions())
