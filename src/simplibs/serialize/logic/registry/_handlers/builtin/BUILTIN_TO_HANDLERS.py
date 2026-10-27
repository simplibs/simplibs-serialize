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
from .....annotations import ToHandler


BUILTIN_TO_HANDLERS: Final[Mapping[Any, ToHandler]] = MappingProxyType({
    # ---- DATE AND TIME ---------------------------------------------------
    datetime: lambda obj: obj.isoformat(),
    date: lambda obj: obj.isoformat(),
    time: lambda obj: obj.isoformat(),
    timedelta: lambda obj: obj.total_seconds(),

    # ---- TEXT-LIKE VALUES ------------------------------------------------
    PurePath: lambda obj: obj.as_posix(),
    UUID: str,
    Decimal: str,
    Fraction: str,

    # ---- BYTES — JSON has no bytes, base64 is the usual text form --------
    bytes: lambda obj: base64.b64encode(obj).decode("ascii"),
    bytearray: lambda obj: base64.b64encode(obj).decode("ascii"),

    # ---- NETWORK ADDRESSES (interfaces are found through their base class)
    IPv4Address: str,
    IPv6Address: str,
    IPv4Network: str,
    IPv6Network: str,

    # ---- ENUM — one key serves every enum, found through the class hierarchy
    Enum: lambda obj: obj.value,
})
"""Read-only table: class → `to_func`. Found through the class hierarchy."""


_DESIGN_NOTES = """
# BUILTIN_TO_HANDLERS — What `serialize` Knows by Heart

## Purpose
The fixed part of the `to_func` table. Nothing writes into it; the live copy is
`TO_HANDLERS`.

## One Key per Family
The lookup walks the class hierarchy, so a few base classes cover everything:
* `PurePath` covers `PosixPath` and `WindowsPath` — the class `Path("x")`
  really has; a table keyed by `Path` would never match it.
* `Enum` covers every enum, so no special branch is needed (every enum is its own
  class; there is no single exact key for all of them).
  A `class Color(str, Enum)` reaches the `Enum` handler because `str` has none.
* `IPv4Address` also serves `IPv4Interface`, which derives from it.
"""
