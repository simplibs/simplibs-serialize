# 🏷️ `annotations` — Types for Your Signatures

The `annotations` package holds the **named types that appear in the signatures** of this library —
and that you need yourself when you write a handler or a function that wraps `serialize`. They
live in the root of `simplibs.serialize`:

```python
from simplibs.serialize import FromHandler, TargetType, ToHandler
```

```python
from simplibs.serialize import ToHandler, register_type, serialize

to_point: ToHandler = lambda p: {"x": p.x, "y": p.y}
register_type(Point, to_func=to_point, from_func=lambda data, target: target(**data))
```

## A note on "hints, not validators"

Unlike the annotations of [`simplibs-file`](https://pypi.org/project/simplibs-file/) or
[`simplibs-path`](https://pypi.org/project/simplibs-path/), **these three are plain type aliases**.
They are there for the reader and for the type checker — they do not carry a predicate, and
`@validate_call` does not check a value against them beyond what the underlying type says. That is
on purpose: there is no sensible runtime check for "any annotation" (`TargetType`).

| Alias         | Is                                                                  | Appears in                                              |
|---------------|---------------------------------------------------------------------|---------------------------------------------------------|
| `ToHandler`   | `Callable[[Any], Any]`                                              | `serialize(default=)`, `register_type(to_func=)`, the actions |
| `FromHandler` | `Callable[[Any, Any], Any]`                                         | `register_type(from_func=)`                             |
| `TargetType`  | `Any`                                                               | the `annotation` parameter of `deserialize` and friends |

`Location` — the path to a value in an error card — is **not** here: nobody outside the library
writes one, so it is a private helper.

---

## 🧭 Table of Contents

* [`ToHandler`](#tohandler)
* [`FromHandler`](#fromhandler)
* [`TargetType`](#targettype)

[⬅️ Back to main README](../README.md#-types-for-your-signatures)

---

### `ToHandler`

The shape of a function that **turns an object into a value `serialize` understands** — the
`to_func` of `register_type` and the `default` of `serialize`.

**Definition:**

```python
ToHandler: TypeAlias = Callable[[Any], Any]
```

**Example usage:**

```python
to_iso: ToHandler = lambda value: value.isoformat()

serialize(obj, default=to_iso)                                   # a fallback for what nothing else knows
register_type(Moment, to_func=lambda m: {"when": m.when, "who": m.who})
```

**The result is serialized again.** The value a handler returns does not have to be JSON-ready:
it may be anything `serialize` itself can handle — a `dict` holding datetimes, a dataclass, an
enum member — and it goes through `serialize` once more. That is what lets a handler stay one line
long. A handler that returns its own argument, or a new value of its own type each time, is a
circle, and is named as one.

<details>
<summary>🔍 Under the hood</summary>

```python
ToHandler: TypeAlias = Callable[[Any], Any]
"""A function `to_func(obj)` that turns an object into a value `serialize` understands."""
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `FromHandler`

The shape of a function that **builds an object back from data** — the `from_func` of
`register_type`.

**Definition:**

```python
FromHandler: TypeAlias = Callable[[Any, Any], Any]
```

**Example usage:**

```python
register_type(Point, to_func=..., from_func=lambda data, target: target(**data))
register_type(PurePath, to_func=str, from_func=lambda data, target: target(data))
```

**The second argument is the annotation.** The handler receives the annotation it was found for,
not only the data. One handler therefore serves a whole family of classes found through their base
class: `lambda data, target: target(data)` builds a `PosixPath`, a `WindowsPath` or any `Path`
subclass the caller asked for.

**Why `Any`, not `type`.** A handler can also be registered for a subscripted annotation such as
`list[int]`, which is not a `type`.

<details>
<summary>🔍 Under the hood</summary>

```python
FromHandler: TypeAlias = Callable[[Any, Any], Any]
"""A function `from_func(data, annotation)` that builds an object back from data."""
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `TargetType`

**The annotation passed to `deserialize`** — a class or a typing construct for it to build:
`Point`, `list[int]`, `int | None`.

**Definition:**

```python
TargetType: TypeAlias = Any
```

**Example usage:**

```python
def load(data: object, target: TargetType) -> object:      # a wrapper around deserialize
    return deserialize(data, target)

load([1, 2], list[int])                                    # -> [1, 2]
load(None, int | None)                                     # -> None
```

**Why it exists.** `type[T]` is wrong for `list[int]` or `int | None` — neither is a class — so the
parameter had no honest name; this alias is the name.

**Why `Any`.** Python has no type that means "any annotation". The alias keeps the signature
readable and makes the real limit visible in one place: what `deserialize` can build is listed in
[its documentation](logic/README_SERIALIZE_DESERIALIZER.md#a-note-on-what-can-be-built), not in the
type. An annotation the library cannot build is a `DESERIALIZE_UNSUPPORTED_ANNOTATION` card at
run time.

<details>
<summary>🔍 Under the hood</summary>

```python
TargetType: TypeAlias = Any
"""A class or typing construct for `deserialize` to build: `Point`, `list[int]`, `int | None`."""
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-types-for-your-signatures)
