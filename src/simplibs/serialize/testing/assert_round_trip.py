import json
from collections.abc import Callable
from typing import Any
from simplibs.exception.testing import maybe_subtest
from simplibs.sentinels import UNSET
# Outers
from ..annotations import TargetType
from ..logic.deserializer import deserialize
from ..logic.json_io import from_json, to_json
from ..logic.serializer import serialize


def _name_of(target: Any) -> str:
    """Readable name of an annotation: `Config`, `list[Point]`, `dict[str, int | None]`."""
    if getattr(target, "__origin__", None) is None and hasattr(target, "__name__"):
        return target.__name__
    return repr(target)


def assert_round_trip(
    subtests: Any,
    value: Any,
    annotation: TargetType = None,
    *,
    strict: bool = True,
    compare: Callable[[Any, Any], bool] | None = None,
    check_json: bool = True,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Assert that a value survives the trip out and back, unchanged.

    Four checks, each reported on its own through `subtests`:
    `serialize` returns valid JSON-compatible data; it returns the same data twice;
    `deserialize(serialize(value), annotation)` equals the value; and, unless
    `check_json` is False, `from_json(to_json(value), annotation)` does too.

    Args:
        subtests: The pytest-subtests fixture. May be None when `verbose=False`.
        value: The value to send out and back.
        annotation: What to build on the way back. Defaults to `type(value)`;
            give it for anything whose type is not the whole annotation
            (`list[Point]`, `dict[str, int | None]`).
        strict: As for `deserialize`.
        compare: How to tell that the result equals the value. Defaults to `==`;
            give one for a type without `__eq__`, or a `nan`.
        check_json: If False, only the structure round trip is checked.
        verbose: If True, each check is an isolated subtest; if False, the first
            failed check raises immediately.
        intro: Optional subtest-name prefix replacing the default `[annotation]`.

    Example:
        def test_config(subtests):
            assert_round_trip(subtests, Config(port=8080, tags={"a", "b"}))
            assert_round_trip(subtests, [Point(1, 2)], list[Point])
    """

    # 1. What to build, how to compare, and how to name the checks
    target = type(value) if annotation is None else annotation
    same = compare if compare is not None else (lambda left, right: left == right)
    prefix = f"{intro} " if intro else f"[{_name_of(target)}] "

    # 2. The way out must give plain, valid JSON data
    data: Any = UNSET
    with maybe_subtest(subtests, name=f"{prefix}serialize returns valid JSON-compatible data", verbose=verbose):
        data = serialize(value)
        json.dumps(data, allow_nan=False)
    if data is UNSET:
        return

    # 3. The same value must always give the same data (sets, key order)
    with maybe_subtest(subtests, name=f"{prefix}serialize returns the same data every time", verbose=verbose):
        again = serialize(value)
        assert again == data, f"two calls gave different data:\n{data!r}\n{again!r}"

    # 4. The way back must give the value again
    with maybe_subtest(subtests, name=f"{prefix}deserialize(serialize(value)) equals the value", verbose=verbose):
        rebuilt = deserialize(data, target, strict=strict)
        assert same(rebuilt, value), f"expected {value!r}, got {rebuilt!r}"

    # 5. The same through JSON text
    if check_json:
        with maybe_subtest(subtests, name=f"{prefix}from_json(to_json(value)) equals the value", verbose=verbose):
            rebuilt = from_json(to_json(value), target, strict=strict)
            assert same(rebuilt, value), f"expected {value!r}, got {rebuilt!r}"


_DESIGN_NOTES = """
# assert_round_trip — Out and Back, Unchanged

## Purpose
The one property every serializable type must have, checked in one call. The
tests of a project that registers its own types need it more than anything.

## `subtests` First, Through `maybe_subtest`
As in `assert_action` and `assert_pattern`: with `verbose=True` every check is
reported separately, so one failing check does not hide the others. With
`verbose=False` no subtest is created (`subtests` may then be `None`) and the
first failed check raises at once.

## Subtest Names
Every name starts with `[annotation]` (`[Config]`, `[list[Point]]`), or with `intro`
when it is given. Without it, two calls in one test (the example above) produced
identical names and a failing report could not say which value failed.

## What Each Check Catches
* Valid JSON data: a handler that returns something `json.dumps` rejects. `json.dumps`
  also accepts a tuple and an integer key (and writes them as a list and a string), so
  the JSON round trip is the check that sees such a change.
* Same data twice: a set or a mapping whose order depends on the run.
* Structure round trip: a handler pair that does not invert each other.
* JSON round trip: what only text can break (a key type, a float, a `bytes`).

## `compare`
`==` is the honest default. A type without `__eq__` (or one with a `nan`) needs
its own idea of "the same", and the caller is the only one who knows it.

## Stops Early
If `serialize` itself fails, the later checks have no data to work with and are
skipped; the first failure is the one to read.
"""
