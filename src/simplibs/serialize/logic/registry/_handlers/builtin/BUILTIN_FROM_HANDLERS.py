import base64
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from pathlib import PurePath
from types import MappingProxyType
from typing import Any, Final
from uuid import UUID
# Outers
from .....annotations import FromHandler


def _from_text(build: FromHandler) -> FromHandler:
    """Wrap a handler so that only text reaches it."""
    def handler(data: Any, target: Any) -> Any:
        if not isinstance(data, str):
            raise TypeError(f"expected text, got {type(data).__name__}")
        return build(data, target)
    return handler


def _from_text_or_int(build: FromHandler) -> FromHandler:
    """Wrap a handler so that only text or a whole number reaches it (no float, no bool)."""
    def handler(data: Any, target: Any) -> Any:
        if isinstance(data, bool) or not isinstance(data, (str, int)):
            raise TypeError(f"expected text or a whole number, got {type(data).__name__}")
        return build(data, target)
    return handler


def _from_number(build: FromHandler) -> FromHandler:
    """Wrap a handler so that only a number reaches it (no bool)."""
    def handler(data: Any, target: Any) -> Any:
        if isinstance(data, bool) or not isinstance(data, (int, float)):
            raise TypeError(f"expected a number, got {type(data).__name__}")
        return build(data, target)
    return handler


BUILTIN_FROM_HANDLERS: Final[Mapping[Any, FromHandler]] = MappingProxyType({
    # ---- DATE AND TIME ---------------------------------------------------
    datetime: _from_text(lambda data, target: target.fromisoformat(data)),
    date: _from_text(lambda data, target: target.fromisoformat(data)),
    time: _from_text(lambda data, target: target.fromisoformat(data)),
    timedelta: _from_number(lambda data, target: target(seconds=data)),

    # ---- TEXT-LIKE VALUES — the target class builds itself from the text -
    PurePath: _from_text(lambda data, target: target(data)),
    UUID: _from_text(lambda data, target: target(data)),
    Decimal: _from_text_or_int(lambda data, target: target(data)),
    Fraction: _from_text_or_int(lambda data, target: target(data)),

    # ---- BYTES — strict base64: stray characters are an error, not skipped
    bytes: _from_text(lambda data, target: target(base64.b64decode(data, validate=True))),
    bytearray: _from_text(lambda data, target: target(base64.b64decode(data, validate=True))),

    # ---- NETWORK ADDRESSES -----------------------------------------------
    IPv4Address: _from_text(lambda data, target: target(data)),
    IPv6Address: _from_text(lambda data, target: target(data)),
    IPv4Network: _from_text(lambda data, target: target(data)),
    IPv6Network: _from_text(lambda data, target: target(data)),

    # ---- ENUM — rebuilt by value; one key serves every enum --------------
    Enum: lambda data, target: target(data),
})
"""Read-only table: class → `from_func`. Found through the class hierarchy."""


_DESIGN_NOTES = """
# BUILTIN_FROM_HANDLERS — What `deserialize` Knows by Heart

## Purpose
The fixed part of the `from_func` table; the live copy is `FROM_HANDLERS`.

## The Target Builds Itself
Every handler calls the annotation it receives (`target(data)`,
`target.fromisoformat(data)`), never a hard-coded class. Asking for a `Path`
gives a `Path`, asking for a `PurePosixPath` gives a `PurePosixPath`, both through
the same `PurePath` entry; the same goes for the enum the caller named.

## Each Handler Guards Its Own Input
The classes accept more than a JSON value should give them: `IPv4Address(5)` is a valid
address, `Decimal(1.1)` is `1.100000000000000088...`, `timedelta(seconds=True)` is one
second. So the kind of data is checked before the class is called, once per group:

* text only — dates, `PurePath`, `UUID`, network addresses, base64 `bytes`;
* text or a whole number — `Decimal`, `Fraction` (never a `float`, never a `bool`);
* a number — `timedelta` (never a `bool`).

A wrong kind raises a plain `TypeError`; `deserialize` catches whatever a handler raises
and turns it into a card with the location and the annotation. `Enum` is left open on
purpose: an enum's values may be of any JSON kind.
"""
