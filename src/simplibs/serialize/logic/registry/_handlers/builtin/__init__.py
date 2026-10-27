from .BUILTIN_FROM_HANDLERS import BUILTIN_FROM_HANDLERS
from .BUILTIN_TO_HANDLERS import BUILTIN_TO_HANDLERS


_DESIGN_NOTES = """
# Built-in Handlers Sub-Package

## Purpose
The types the library handles without being told: dates and times, paths, UUIDs,
decimals, fractions, bytes, IP addresses and every enum.

## Internal Components Registry

| Component               | Type     | Description                                       |
| :---------------------- | :------- | :------------------------------------------------ |
| `BUILTIN_TO_HANDLERS`   | Constant | Read-only table: class → `to_func`.              |
| `BUILTIN_FROM_HANDLERS` | Constant | Read-only table: class → `from_func`.            |

## What Is Written Where

| Type                                  | In the data                        |
| :------------------------------------ | :--------------------------------- |
| `datetime`, `date`, `time`            | ISO 8601 text                      |
| `timedelta`                           | seconds (a number)                 |
| `PurePath` and its subclasses         | text with `/` separators           |
| `UUID`, `Decimal`, `Fraction`         | text                               |
| `bytes`, `bytearray`                  | base64 text                        |
| `IPv4/IPv6 Address`, `Network`        | text                               |
| every `Enum`                          | the member's value                 |
"""
