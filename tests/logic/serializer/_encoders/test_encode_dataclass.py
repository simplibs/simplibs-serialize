from dataclasses import dataclass, field
from datetime import date

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import SerializationError, serialized_field
from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_dataclass, encode_value


@dataclass
class Plain:
    zeta: int
    alpha: str
    middle: list


@dataclass
class Aliased:
    user_name: str = serialized_field(alias="userName")
    age: int = 0


@dataclass
class WithSecret:
    name: str
    secret: str = serialized_field(exclude=True, default="")


@dataclass
class Clash:
    first: int = serialized_field(alias="x")
    second: int = serialized_field(alias="x")


@dataclass
class ClashWithPlainName:
    x: int
    y: int = serialized_field(alias="x")


@dataclass
class ExcludedClash:
    first: int = serialized_field(alias="x", exclude=True)
    second: int = serialized_field(alias="x")


@dataclass
class Inner:
    value: int


@dataclass
class Outer:
    inner: Inner
    day: date


@dataclass(slots=True)
class Slotted:
    a: int
    b: str


@dataclass
class WithInitFalse:
    a: int
    computed: int = field(init=False, default=7)


@dataclass
class BrokenOptions:
    value: int = field(default=0, metadata={"simplibs.serialize": {"alais": "x"}})


def _fake_context():
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_encode_value(obj, location, context):
        calls.append((obj, location))
        return obj

    return SerializeContext(default=None, allow_nan=False, encode_value=fake_encode_value), calls


def _real_context() -> SerializeContext:
    return SerializeContext(default=None, allow_nan=False, encode_value=encode_value)


def test_fields_come_in_declaration_order():
    context, _ = _fake_context()

    result = encode_dataclass(Plain(1, "a", [2]), (), context)

    assert list(result) == ["zeta", "alpha", "middle"]
    assert result == {"zeta": 1, "alpha": "a", "middle": [2]}
    assert type(result) is dict


def test_every_value_is_converted_below_its_name():
    context, calls = _fake_context()

    encode_dataclass(Plain(1, "a", [2]), ("rows", 0), context)

    assert calls == [
        (1, ("rows", 0, "zeta")),
        ("a", ("rows", 0, "alpha")),
        ([2], ("rows", 0, "middle")),
    ]


def test_a_field_is_written_under_its_alias():
    context, calls = _fake_context()

    result = encode_dataclass(Aliased("ann", 5), (), context)

    assert result == {"userName": "ann", "age": 5}
    assert ("ann", ("userName",)) in calls


def test_an_excluded_field_is_left_out():
    context, calls = _fake_context()

    result = encode_dataclass(WithSecret("ann", "hidden"), (), context)

    assert result == {"name": "ann"}
    assert all(value != "hidden" for value, _ in calls)


def test_a_field_that_is_not_part_of_init_is_written():
    context, _ = _fake_context()

    assert encode_dataclass(WithInitFalse(1), (), context) == {"a": 1, "computed": 7}


def test_a_slots_dataclass_is_written():
    context, _ = _fake_context()

    assert encode_dataclass(Slotted(1, "x"), (), context) == {"a": 1, "b": "x"}


@pytest.mark.parametrize("obj", [Clash(1, 2), ClashWithPlainName(1, 2)], ids=["two_aliases", "alias_and_name"])
def test_two_fields_with_one_name_in_the_data_are_an_error(obj):
    context, _ = _fake_context()

    with pytest.raises(SerializationError) as caught:
        encode_dataclass(obj, ("row",), context)

    assert caught.value.error_name == "SERIALIZE_DUPLICATE_KEY"
    assert caught.value.label == "$.row"
    assert caught.value.value == "x"


def test_an_excluded_field_does_not_take_its_alias_away_from_another():
    context, _ = _fake_context()

    assert encode_dataclass(ExcludedClash(1, 2), (), context) == {"x": 2}


def test_nested_dataclasses_and_handler_types_are_converted():
    result = encode_dataclass(Outer(Inner(1), date(2026, 1, 2)), (), _real_context())

    assert result == {"inner": {"value": 1}, "day": "2026-01-02"}


def test_the_location_of_a_failing_value_uses_the_name_in_the_data():
    obj = Aliased(user_name=object())

    with pytest.raises(SerializationError) as caught:
        encode_dataclass(obj, (), _real_context())

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_TYPE"
    assert caught.value.label == "$.userName"


def test_broken_field_options_are_a_param_error():
    context, _ = _fake_context()

    with pytest.raises(ParamError):
        encode_dataclass(BrokenOptions(), (), context)
