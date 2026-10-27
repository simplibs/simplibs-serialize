from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, Flag, IntEnum
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


class Name(str, Enum):
    ANN = "ann"


class Permission(Flag):
    READ = 1
    WRITE = 2


_ENTRIES = [
    pytest.param(datetime, datetime(2026, 1, 2, 3, 4, 5), "2026-01-02T03:04:05", id="datetime"),
    pytest.param(date, date(2026, 1, 2), "2026-01-02", id="date"),
    pytest.param(time, time(3, 4, 5), "03:04:05", id="time"),
    pytest.param(timedelta, timedelta(minutes=1, seconds=30), 90.0, id="timedelta"),
    pytest.param(PurePath, PurePosixPath("a/b"), "a/b", id="posix_path"),
    pytest.param(PurePath, PureWindowsPath("a\\b"), "a/b", id="windows_path"),
    pytest.param(UUID, UUID(int=1), "00000000-0000-0000-0000-000000000001", id="uuid"),
    pytest.param(Decimal, Decimal("1.10"), "1.10", id="decimal"),
    pytest.param(Fraction, Fraction(1, 3), "1/3", id="fraction"),
    pytest.param(bytes, b"hi", "aGk=", id="bytes"),
    pytest.param(bytearray, bytearray(b"hi"), "aGk=", id="bytearray"),
    pytest.param(IPv4Address, IPv4Address("1.2.3.4"), "1.2.3.4", id="ipv4_address"),
    pytest.param(IPv6Address, IPv6Address("::1"), "::1", id="ipv6_address"),
    pytest.param(IPv4Network, IPv4Network("10.0.0.0/8"), "10.0.0.0/8", id="ipv4_network"),
    pytest.param(IPv6Network, IPv6Network("fe80::/10"), "fe80::/10", id="ipv6_network"),
    pytest.param(Enum, Color.RED, "red", id="enum"),
]


def test_is_read_only():
    with pytest.raises(TypeError):
        BUILTIN_TO_HANDLERS[int] = str


def test_knows_exactly_these_classes():
    assert set(BUILTIN_TO_HANDLERS) == {
        datetime, date, time, timedelta, PurePath, UUID, Decimal, Fraction, bytes, bytearray,
        IPv4Address, IPv6Address, IPv4Network, IPv6Network, Enum,
    }


def test_every_class_can_also_be_read_back():
    assert set(BUILTIN_TO_HANDLERS) == set(BUILTIN_FROM_HANDLERS)


@pytest.mark.parametrize("key, obj, expected", _ENTRIES)
def test_handler_of_each_entry(key, obj, expected):
    result = BUILTIN_TO_HANDLERS[key](obj)

    assert result == expected
    assert type(result) is type(expected)


# ---------- found through the class hierarchy ----------

def test_a_real_path_is_found_through_purepath():
    path_class = type(Path("a/b"))

    handler = find_handler(BUILTIN_TO_HANDLERS, path_class)

    assert handler is BUILTIN_TO_HANDLERS[PurePath]
    assert handler(Path("a/b")) == "a/b"


def test_datetime_is_not_handled_as_a_date():
    handler = find_handler(BUILTIN_TO_HANDLERS, datetime)

    assert handler is BUILTIN_TO_HANDLERS[datetime]
    assert handler is not BUILTIN_TO_HANDLERS[date]
    assert "T" in handler(datetime(2026, 1, 2, 3, 4, 5))


def test_an_interface_is_found_through_its_address_class():
    handler = find_handler(BUILTIN_TO_HANDLERS, IPv4Interface)

    assert handler is BUILTIN_TO_HANDLERS[IPv4Address]
    assert handler(IPv4Interface("1.2.3.4/24")) == "1.2.3.4/24"


@pytest.mark.parametrize(
    "member, value",
    [
        pytest.param(Color.RED, "red", id="plain_enum"),
        pytest.param(Level.LOW, 1, id="int_enum"),
        pytest.param(Name.ANN, "ann", id="str_enum"),
        pytest.param(Permission.READ | Permission.WRITE, 3, id="flag_combination"),
    ],
)
def test_every_kind_of_enum_gives_its_value(member, value):
    handler = find_handler(BUILTIN_TO_HANDLERS, type(member))

    assert handler is BUILTIN_TO_HANDLERS[Enum]
    result = handler(member)
    assert result == value
    assert type(result) is type(value)


@pytest.mark.parametrize("cls", [int, str, list, dict, type(None)], ids=lambda cls: cls.__name__)
def test_plain_json_classes_have_no_handler(cls):
    assert find_handler(BUILTIN_TO_HANDLERS, cls) is None


def test_bytes_survive_the_trip_through_the_from_table():
    raw = bytes(range(256))

    text = BUILTIN_TO_HANDLERS[bytes](raw)

    assert BUILTIN_FROM_HANDLERS[bytes](text, bytes) == raw
