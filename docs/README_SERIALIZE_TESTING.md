# 🧪 `testing` — Test Your Own Types

The `testing` package holds one function for **the one property every serializable type must
have**: what goes out comes back unchanged. If your project registers its own types with
[`register_type`](../logic/README_SERIALIZE_REGISTRY.md), or declares dataclasses with aliases and
exclusions, this is the test you want most — and it is one call.

```python
from simplibs.serialize.testing import assert_round_trip

def test_config(subtests):
    assert_round_trip(subtests, Config(port=8080, tags={"a", "b"}))
    assert_round_trip(subtests, [Point(1, 2)], list[Point])
```

`testing` is **not** exported from `simplibs.serialize` itself — it is a domain of its own, imported
through `simplibs.serialize.testing`. It needs the `subtests` fixture, which is built into
pytest since version 9.0 — the same way `assert_action` and `assert_pattern` of the other libraries
use it.

## A note on "`subtests` first"

Every check is reported **separately** through `subtests`, so one failing check does not hide the
others: a handler pair that does not invert each other and a set whose order changes with the run
are two lines in the report, not one. The function does not raise — a failed check is a failed
subtest.

## A note on what each check catches

| # | Check                                           | What it catches                                                        |
|---|-------------------------------------------------|------------------------------------------------------------------------|
| 1 | `serialize` returns valid JSON-compatible data  | A handler that returns something `json.dumps` rejects.                 |
| 2 | `serialize` returns the same data every time    | A set or a mapping whose order depends on the run.                     |
| 3 | `deserialize(serialize(value))` equals the value | A pair of handlers that do not invert each other; a field lost on the way. |
| 4 | `from_json(to_json(value))` equals the value    | What only text can break: a key type, a float, `bytes`.                |

The fourth check can be switched off (`check_json=False`) when only the structure matters.

## A note on stopping early

If `serialize` itself fails, the later checks have no data to work with and are **skipped** — the
first failure is the one to read.

---

## 🧭 Table of Contents

* [`assert_round_trip`](#assert_round_trip)

[⬅️ Back to main README](../../README.md#-testing--test-your-own-types)

---

### `assert_round_trip`

Asserts that a value survives the trip out and back, unchanged.

**Parameters:**

* `subtests` (*Any*): The `subtests` fixture of pytest 9+.
* `value` (*Any*): The value to send out and back.
* `annotation` (*TargetType*, default `None`): What to build on the way back. Defaults to `type(value)`; give it for anything whose type is not the whole annotation (`list[Point]`, `dict[str, int | None]`).
* `strict` (*bool*, keyword-only, default `True`): As for `deserialize`.
* `compare` (*Callable[[Any, Any], bool] | None*, keyword-only, default `None`): How to tell that the result equals the value. Defaults to `==`; give one for a type without `__eq__`, or whose values never compare equal.
* `check_json` (*bool*, keyword-only, default `True`): If `False`, only the structure round trip is checked (checks 1 to 3).

**Returns:**

* `None`: Everything is reported through `subtests`.

**Raises:**

* Nothing itself: a failing check is reported as a failed subtest, with the message of the assertion or the card that failed.

**Example usage:**

```python
def test_point(subtests):
    assert_round_trip(subtests, Point(1, 2))                     # annotation: Point

def test_points(subtests):
    assert_round_trip(subtests, [Point(1, 2)], list[Point])      # the type of the value is just `list`

def test_session(subtests):
    # `Session` has no `__eq__`: say what "the same" means
    assert_round_trip(
        subtests,
        Session(user="eva", token="x"),
        compare=lambda a, b: (a.user, a.token) == (b.user, b.token),
    )

def test_structure_only(subtests):
    assert_round_trip(subtests, Config(port=8080), check_json=False)   # skip check 4
```

**A registered type needs its handlers undone.** A registration is global, so register the type in
a fixture and remove it afterwards — otherwise it leaks into every other test:

```python
@pytest.fixture
def moment_registered():
    register_type(Moment, to_func=lambda m: {"at": m.at}, from_func=lambda d, t: t(d["at"]))
    yield
    unregister_type(Moment)

def test_moment(subtests, moment_registered):
    assert_round_trip(subtests, Moment(datetime(2024, 1, 2)))
```

**Why `compare` exists.** `==` is the honest default. A type without `__eq__`, or one whose instances
never compare equal, needs its own idea of "the same", and the caller is the only one who knows it.

<details>
<summary>🔍 Under the hood</summary>

```python
# 1. What to build, and how to compare
target = type(value) if annotation is None else annotation
same = compare if compare is not None else (lambda left, right: left == right)

# 2. The way out must give plain, valid JSON data
data: Any = UNSET
with subtests.test(msg="serialize returns valid JSON-compatible data"):
    data = serialize(value)
    json.dumps(data, allow_nan=False)
if data is UNSET:                       # nothing to continue with
    return

# 3. The same value must always give the same data (sets, key order)
with subtests.test(msg="serialize returns the same data every time"):
    again = serialize(value)
    assert again == data, f"two calls gave different data:\n{data!r}\n{again!r}"

# 4. The way back must give the value again
with subtests.test(msg="deserialize(serialize(value)) equals the value"):
    rebuilt = deserialize(data, target, strict=strict)
    assert same(rebuilt, value), f"expected {value!r}, got {rebuilt!r}"

# 5. The same through JSON text
if check_json:
    with subtests.test(msg="from_json(to_json(value)) equals the value"):
        rebuilt = from_json(to_json(value), target, strict=strict)
        assert same(rebuilt, value), f"expected {value!r}, got {rebuilt!r}"
```

</details>

> 💡 The first check runs `serialize` with its defaults, so a `nan` in the value is reported
> there — as the `SERIALIZE_NON_FINITE_NUMBER` card it is — and not three checks later as a
> mysterious inequality (`nan != nan`).

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-testing--test-your-own-types)
