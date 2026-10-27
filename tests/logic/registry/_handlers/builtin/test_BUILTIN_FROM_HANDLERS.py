from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, IntEnum
from fractions import Fraction
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Network
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from uuid import UUID

import pytest

from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_FROM_HANDLERS, BUILTIN_TO_HANDLERS
from simplibs.serialize.logic.registry._helpers import find_handler


class Color(Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


class Ratio(Enum):
    HALF = 0.5


class MyDate(date):
    """A date subclass: the target must build itself."""


_ENTRIES = [
    pytest.param(datetime, "2026-01-02T03:04:05", datetime, datetime(2026, 1, 2, 3, 4, 5), id="datetime"),
    pytest.param(date, "2026-01-02", date, date(2026, 1, 2), id="date"),
    pytest.param(time, "03:04:05", time, time(3, 4, 5), id="time"),
    pytest.param(timedelta, 90, timedelta, timedelta(seconds=90), id="timedelta_from_int"),
    pytest.param(timedelta, 90.5, timedelta, timedelta(seconds=90.5), id="timedelta_from_float"),
    pytest.param(PurePath, "a/b", PurePosixPath, PurePosixPath("a/b"), id="posix_path"),
    pytest.param(PurePath, "a\\b", PureWindowsPath, PureWindowsPath("a\\b"), id="windows_path"),
    pytest.param(UUID, "00000000-0000-0000-0000-000000000001", UUID, UUID(int=1), id="uuid"),
    pytest.param(Decimal, "1.10", Decimal, Decimal("1.10"), id="decimal_from_text"),
    pytest.param(Decimal, 5, Decimal, Decimal(5), id="decimal_from_int"),
    pytest.param(Fraction, "1/3", Fraction, Fraction(1, 3), id="fraction_from_text"),
    pytest.param(Fraction, 2, Fraction, Fraction(2), id="fraction_from_int"),
    pytest.param(bytes, "aGk=", bytes, b"hi", id="bytes"),
    pytest.param(bytearray, "aGk=", bytearray, bytearray(b"hi"), id="bytearray"),
    pytest.param(IPv4Address, "1.2.3.4", IPv4Address, IPv4Address("1.2.3.4"), id="ipv4_address"),
    pytest.param(IPv6Address, "::1", IPv6Address, IPv6Address("::1"), id="ipv6_address"),
    pytest.param(IPv4Network, "10.0.0.0/8", IPv4Network, IPv4Network("10.0.0.0/8"), id="ipv4_network"),
    pytest.param(IPv6Network, "fe80::/10", IPv6Network, IPv6Network("fe80::/10"), id="ipv6_network"),
    pytest.param(Enum, "red", Color, Color.RED, id="text_enum"),
    pytest.param(Enum, 1, Level, Level.LOW, id="int_enum"),
]


def test_is_read_only():
    with pytest.raises(TypeError):
        BUILTIN_FROM_HANDLERS[int] = str


def test_knows_the_same_classes_as_the_to_table():
    assert set(BUILTIN_FROM_HANDLERS) == set(BUILTIN_TO_HANDLERS)


@pytest.mark.parametrize("key, data, target, expected", _ENTRIES)
def test_handler_of_each_entry(key, data, target, expected):
    result = BUILTIN_FROM_HANDLERS[key](data, target)

    assert result == expected
    assert type(result) is target


# ---------- the target builds itself ----------

def test_a_real_path_class_gives_a_real_path():
    path_class = type(Path("a/b"))

    handler = find_handler(BUILTIN_FROM_HANDLERS, path_class)

    assert handler is BUILTIN_FROM_HANDLERS[PurePath]
    assert handler("a/b", path_class) == Path("a/b")


def test_an_interface_is_found_through_its_address_class():
    handler = find_handler(BUILTIN_FROM_HANDLERS, IPv4Interface)

    result = handler("1.2.3.4/24", IPv4Interface)

    assert handler is BUILTIN_FROM_HANDLERS[IPv4Address]
    assert type(result) is IPv4Interface
    assert result == IPv4Interface("1.2.3.4/24")


def test_a_subclass_of_date_gives_that_subclass():
    handler = find_handler(BUILTIN_FROM_HANDLERS, MyDate)

    result = handler("2026-01-02", MyDate)

    assert handler is BUILTIN_FROM_HANDLERS[date]
    assert type(result) is MyDate


# ---------- text that is not what the class can read ----------

@pytest.mark.parametrize("text", ["@@", "aG k=", "aGk"], ids=["stray_characters", "inner_space", "missing_padding"])
@pytest.mark.parametrize("key", [bytes, bytearray], ids=["bytes", "bytearray"])
def test_invalid_base64_raises(key, text):
    with pytest.raises(ValueError):
        BUILTIN_FROM_HANDLERS[key](text, key)


def test_a_datetime_text_asked_as_a_date_raises():
    with pytest.raises(ValueError):
        BUILTIN_FROM_HANDLERS[date]("2026-01-02T03:04:05", date)


def test_a_text_that_is_no_date_raises():
    with pytest.raises(ValueError):
        BUILTIN_FROM_HANDLERS[datetime]("not a date", datetime)


# ---------- each handler guards its own input ----------

_TEXT = "expected text, got"
_TEXT_OR_INT = "expected text or a whole number, got"
_NUMBER = "expected a number, got"

_WRONG_KIND = [
    pytest.param(datetime, 5, datetime, _TEXT, id="datetime_from_int"),
    pytest.param(date, 5, date, _TEXT, id="date_from_int"),
    pytest.param(time, 5, time, _TEXT, id="time_from_int"),
    pytest.param(PurePath, 5, PurePosixPath, _TEXT, id="path_from_int"),
    pytest.param(UUID, 5, UUID, _TEXT, id="uuid_from_int"),
    pytest.param(bytes, 5, bytes, _TEXT, id="bytes_from_int"),
    pytest.param(bytearray, 5, bytearray, _TEXT, id="bytearray_from_int"),
    pytest.param(IPv4Address, 5, IPv4Address, _TEXT, id="ipv4_address_from_int"),
    pytest.param(IPv6Address, 5, IPv6Address, _TEXT, id="ipv6_address_from_int"),
    pytest.param(IPv4Network, 5, IPv4Network, _TEXT, id="ipv4_network_from_int"),
    pytest.param(IPv6Network, 5, IPv6Network, _TEXT, id="ipv6_network_from_int"),
    pytest.param(Decimal, 1.1, Decimal, _TEXT_OR_INT, id="decimal_from_float"),
    pytest.param(Decimal, True, Decimal, _TEXT_OR_INT, id="decimal_from_bool"),
    pytest.param(Fraction, 1.5, Fraction, _TEXT_OR_INT, id="fraction_from_float"),
    pytest.param(Fraction, True, Fraction, _TEXT_OR_INT, id="fraction_from_bool"),
    pytest.param(timedelta, True, timedelta, _NUMBER, id="timedelta_from_bool"),
    pytest.param(timedelta, "5", timedelta, _NUMBER, id="timedelta_from_text"),
]


@pytest.mark.parametrize("key, data, target, message", _WRONG_KIND)
def test_the_wrong_kind_of_data_raises_type_error(key, data, target, message):
    with pytest.raises(TypeError) as caught:
        BUILTIN_FROM_HANDLERS[key](data, target)

    assert message in str(caught.value)


def test_an_enum_is_left_open_to_any_kind_of_value():
    assert BUILTIN_FROM_HANDLERS[Enum](0.5, Ratio) is Ratio.HALF


def test_an_enum_refuses_a_value_it_does_not_have():
    with pytest.raises(ValueError):
        BUILTIN_FROM_HANDLERS[Enum]("blue", Color)
