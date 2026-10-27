# 🧩 `logic/registry` — Teach It Your Types

The `registry` package is the **table of types the library knows how to convert**. It holds what
`serialize` and `deserialize` know by heart — dates, paths, UUIDs, decimals, bytes, network
addresses and every enum — and the two functions that let you **add a type of your own** or
**replace** one of the built-in ones, and take it away again.

```python
from simplibs.serialize import register_type, unregister_type

register_type(
    Point,
    to_func=lambda p: {"x": p.x, "y": p.y},
    from_func=lambda data, cls: cls(data["x"], data["y"]),
)

serialize(Point(1, 2))                         # -> {"x": 1, "y": 2}
deserialize({"x": 1, "y": 2}, Point)           # -> Point(x=1, y=2)

unregister_type(Point)                         # the table is as it was before
```

Both functions are wrapped in `@validate_call`. A type is registered **globally** — for the whole
process — which is exactly why there is a function to take it away again.

## A note on what is known by heart

The built-in handlers are fixed — nothing writes into them; the live table is a copy, so a
registration never changes what the library shipped with.

| Type                                              | Written as                         | Read back from                                                  |
|---------------------------------------------------|------------------------------------|-----------------------------------------------------------------|
| `datetime`, `date`, `time`                        | ISO text (`"2024-01-02"`)          | text, through `fromisoformat`                                   |
| `timedelta`                                       | seconds, a number                  | a number (an `int` or a `float`, never a `bool`)                |
| `PurePath` and its family (`Path`, `PosixPath`, …)| text with `/` (`as_posix`)         | text — the **class you ask for** is built (`Path`, `PurePosixPath`, …) |
| `UUID`                                            | text                               | text                                                            |
| `Decimal`, `Fraction`                             | text (exact)                       | text or a whole number — never a `float`, never a `bool`        |
| `bytes`, `bytearray`                              | base64 text                        | base64 text, **strict**: a stray character is an error          |
| `IPv4Address`, `IPv6Address`, `IPv4Network`, `IPv6Network` | text                      | text                                                            |
| every `Enum` (also `IntEnum`, `StrEnum`, `Flag`)  | the member's **value**             | the value, any JSON kind — the member is rebuilt                |

Each reading handler **guards its own input** — the classes accept more than a JSON value should
give them: `IPv4Address(5)` is a valid address, `Decimal(1.1)` is
`1.100000000000000088…`, `timedelta(seconds=True)` is one second. So the *kind* of data is checked
before the class is called, and a wrong kind becomes a `DESERIALIZE_BUILD_FAILED` card with the
location. `Enum` is left open on purpose, because an enum's values may be of any JSON kind.

## A note on how a handler is found

The lookup is **an exact match first, then the nearest base class**. That is why a few entries
cover so much:

* `PurePath` serves `PosixPath` and `WindowsPath` — the class `Path("x")` really has; a table keyed
  by `Path` would never match it.
* `Enum` serves **every** enum — each enum is its own class, so there is no single exact key — and a
  `class Color(str, Enum)` reaches it because `str` has no handler.
* `IPv4Address` also serves `IPv4Interface`, which derives from it.
* `datetime` does **not** find `date`'s handler: it has its own entry, and walking the class
  hierarchy from the front reaches it first.

The same holds for your own types: a handler registered for a base class is used for its
subclasses, **unless a subclass has a handler of its own**, and the nearest one wins. A subscripted
annotation (`list[int]`) has no class hierarchy, so for it the match is **exact only**.

A **handler comes before every general rule**. Whatever you register for a class wins over the
rule for the `dict`, `list` or dataclass it happens to derive from — and over the way a `NewType`
or an exact annotation such as `list[int]` would be built.

## A note on the two handlers

| | `to_func` (`ToHandler`) | `from_func` (`FromHandler`) |
|---|---|---|
| Called as | `to_func(obj)` | `from_func(data, annotation)` |
| Found by | the class of the object, `type(obj)` | the annotation the caller wrote |
| Works for | a **class** only | a class, a subscripted annotation (`list[int]`), a `NewType` |
| Returns | anything `serialize` understands — it is converted **again** | the built object |

* **The result of `to_func` is converted again**, so it can stay one line long
  (`lambda m: {"when": m.when, "who": m.who}`) — a `dict` holding dates, a dataclass, an enum member.
* **`from_func` receives the annotation**, not only the data, so one handler serves a whole family:
  `lambda data, target: target(data)` builds a `PosixPath`, a `WindowsPath` or whichever `Path`
  subclass was asked for.
* **A class never receives `None`.** `deserialize(None, Point)` is refused before the handler is
  called; `None` belongs to the annotation (`Point | None`), never to the data.
* **A handler is not a guard.** Anything it raises becomes one card with the location —
  `SERIALIZE_HANDLER_FAILED` on the way out, `DESERIALIZE_BUILD_FAILED` on the way back — with the
  original exception as its cause. A library error (`SerializeError`) passes unchanged.

## A note on replacing and removing

Registering `datetime` **replaces** the built-in handler for it — on purpose: a project that wants
epoch seconds instead of ISO text can have them. `unregister_type` puts the built-in one **back**;
it never deletes it, because a library that cannot handle datetimes any more would be worse than
one that uses the default. A type the library knows nothing about is simply forgotten.

Because the table is global, a **test that registers a type must unregister it** — see
[`assert_round_trip`](../testing/README_SERIALIZE_TESTING.md#assert_round_trip) for a fixture that
does exactly that.

## A note on errors

| Situation                                                       | Exception    |
|-----------------------------------------------------------------|--------------|
| No handler is given; `type_` is not a type; it is not hashable; `to_func` for something that is not a class | `ParamError` |

Every one is raised **before anything is stored** — a failed registration changes nothing.

---

## 🧭 Table of Contents

* [`register_type`](#register_type)
* [`unregister_type`](#unregister_type)
* [The helpers behind them](#the-helpers-behind-them)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../../README.md#-logicregistry--teach-it-your-types)

---

### `register_type`

Teaches the library a type of your own — or replaces a built-in handler.

**Parameters:**

* `type_` (*Any*): A class (`Point`), a subscripted annotation (`list[int]`) or a `NewType`. A handler registered for a class is used for its subclasses as well, unless they have a handler of their own.
* `to_func` (*ToHandler | None*, keyword-only, default `None`): Called as `to_func(obj)` by `serialize`. It may return anything `serialize` itself understands. Needs a class as `type_`.
* `from_func` (*FromHandler | None*, keyword-only, default `None`): Called as `from_func(data, annotation)` by `deserialize`.

**Returns:**

* `None`: The handlers are stored in the live table.

**Raises:**

* `ParamError` (`SERIALIZE_REGISTER_NO_HANDLER`): Neither `to_func` nor `from_func` is given.
* `ParamError` (`SERIALIZE_REGISTER_NOT_A_TYPE`): `type_` is not a class, a subscripted annotation or a `NewType` (a string or an instance, for example).
* `ParamError` (`SERIALIZE_REGISTER_UNHASHABLE_TYPE`): `type_` cannot be a key of the registry (`Annotated[int, []]`).
* `ParamError` (`SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS`): `to_func` is given for something that is not a class (`list[int]`, a `NewType`).

**Example usage:**

```python
# both directions for a class
register_type(
    Point,
    to_func=lambda p: {"x": p.x, "y": p.y},
    from_func=lambda data, cls: cls(data["x"], data["y"]),
)

# one direction is enough — here only reading
register_type(UserId, from_func=lambda data, annotation: UserId(int(data)))    # a NewType: from_func only
register_type(list[int], from_func=lambda data, annotation: sorted(data))      # an exact annotation

# a handler for a base class serves its subclasses
register_type(Shape, to_func=lambda s: {"kind": type(s).__name__, "area": s.area()})
serialize(Circle(2))                                   # -> {"kind": "Circle", "area": 12.56...}

# replace a built-in
register_type(
    datetime,
    to_func=lambda d: d.timestamp(),
    from_func=lambda data, cls: cls.fromtimestamp(data),
)
serialize(datetime(2024, 1, 2))                        # -> a number of seconds since the epoch, not ISO text

register_type(Point)                                   # -> raises: SERIALIZE_REGISTER_NO_HANDLER
register_type("Point", to_func=str)                    # -> raises: SERIALIZE_REGISTER_NOT_A_TYPE
register_type(list[int], to_func=sorted)               # -> raises: SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS
```

**Why `to_func` needs a class.** `serialize` looks a handler up by `type(obj)` — the class of the
object it holds. `list[int]` is never the class of anything, so a `to_func` registered for it
could not ever be found. For reading, the key is what the caller **wrote** as the target type, and
`list[int]` or a `NewType` is exactly that.

**Why the key is checked.** `deserialize` looks handlers up by the annotation the caller wrote, so
the only keys that can ever match are the things a caller writes there. A string or an instance
stored as a key would never be found — it is refused at the door instead of failing silently
later.

**Under the hood:**
```python
# 1. Nothing to register
if to_func is None and from_func is None:
    raise_no_handler_error()

# 2. The key must be something the lookup can ever meet
if not is_registrable_type(type_):
    raise_not_registrable_type_error(type_)

# 3. The key must be hashable (a subscripted annotation can carry unhashable metadata)
try:
    hash(type_)
except TypeError:
    raise_unhashable_type_error(type_)

# 4. `to_func` is found by the class of the object, so it needs a class
if to_func is not None and not is_plain_class(type_):
    raise_to_func_needs_class_error(type_)

# 5. Store each handler that was given — only now does the table change
if to_func is not None:
    TO_HANDLERS[type_] = to_func
if from_func is not None:
    FROM_HANDLERS[type_] = from_func
```

> 💡 Registering **only one** direction leaves the other as it was: a `to_func` for a built-in type
> does not touch its built-in reader, and the other way round.

[▲ Back to top](#-table-of-contents)

---

### `unregister_type`

Removes the registration of a type, in **both** directions — the table is as it was before the
call.

**Parameters:**

* `type_` (*Any*): The same class or annotation that was given to `register_type`.

**Returns:**

* `bool`: `True` if anything changed, `False` if there was nothing to remove or restore.

**Example usage:**

```python
register_type(Point, to_func=..., from_func=...)
unregister_type(Point)                                 # -> True    (removed)
unregister_type(Point)                                 # -> False   (nothing to remove — no error)

register_type(datetime, to_func=lambda d: d.timestamp(), from_func=...)
unregister_type(datetime)                              # -> True    (the built-in ISO handler is back)

unregister_type(date)                                  # -> False   (untouched built-in)
unregister_type(list[int])                             # -> False   (an annotation that was never registered)
```

**Not an error to call twice.** A test teardown runs whether or not the test got far enough to
register, so it must be safe to run twice — it returns `False` and raises nothing.

**Both directions at once.** `register_type` can set only one handler, but a half-removed type is
only confusing, so both sides are reset. A built-in handler that was replaced **comes back** and is
never deleted.

**Under the hood:**
```python
# 1. Both directions are reset — never stop after the first one
to_changed = reset_handler(TO_HANDLERS, BUILTIN_TO_HANDLERS, type_)
from_changed = reset_handler(FROM_HANDLERS, BUILTIN_FROM_HANDLERS, type_)

# 2. Report whether the table differs from before the call
return to_changed or from_changed
```

> 💡 Remember the order of `or`: both calls are already made when the result is computed — the
> second direction is never skipped because the first one changed something.

[▲ Back to top](#-table-of-contents)

---

### The helpers behind them

Small internal helpers (not exported) carry the work. The core never sees the table itself — it
asks the two `find_…` functions, so nothing in `serialize` or `deserialize` can change the registry
by accident.

| Helper                                   | What it does                                                             | Used by                          |
|------------------------------------------|--------------------------------------------------------------------------|----------------------------------|
| `find_to_handler(type_)`                 | The handler `serialize` uses for a class — exact, then nearest base.     | `serialize` (`encode_structure`) |
| `find_from_handler(annotation)`          | The handler `deserialize` uses for an annotation.                        | `deserialize` (`build_value`)    |
| `find_handler(handlers, target)`         | The one lookup both of them are built on.                                | the two above                    |
| `is_plain_class(target)`                 | A real class — not `list[int]`, not `int \| str`, not an instance.       | `find_handler`, `register_type`  |
| `is_registrable_type(target)`            | A class, a subscripted annotation or a `NewType`.                        | `register_type`                  |
| `reset_handler(live, builtin, key)`      | One entry, one direction: restore the built-in or remove the registration. | `unregister_type`              |
| `BUILTIN_TO_HANDLERS`, `BUILTIN_FROM_HANDLERS` | The fixed tables (read-only).                                      | the live tables, `reset_handler` |
| `TO_HANDLERS`, `FROM_HANDLERS`           | The live tables — a copy of the built-in ones that `register_type` writes into. | the lookup, the registration |

**`find_handler`** is the exact match, then the nearest base class — the class hierarchy is ordered
from the most to the least specific, so the first registered base is the nearest one and no special
ordering rule is needed anywhere:

```python
# 1. Exact match — the only kind of match a subscripted annotation can have
try:
    exact = handlers.get(target)
except TypeError:                                  # `Annotated[int, <unhashable>]` — simply nothing registered
    return None
if exact is not None:
    return exact

# 2. Only a real class has a class hierarchy to walk
if not is_plain_class(target):
    return None

# 3. The first registered base along the hierarchy is the nearest one
for base in target.__mro__[1:]:
    inherited = handlers.get(base)
    if inherited is not None:
        return inherited

# 4. Nothing registered anywhere along the hierarchy
return None
```

**`is_plain_class` and `is_registrable_type`** decide what may be a key. `list[int]` is not a class —
on some Python versions `isinstance` claims it is, so the origin is asked as well:

```python
# is_plain_class
return isinstance(target, type) and get_origin(target) is None

# is_registrable_type
if is_plain_class(target):                        # a real class
    return True
if get_origin(target) is not None:                # `list[int]`, `Annotated[...]`, `int | None`
    return True
return callable(target) and hasattr(target, "__supertype__")      # a NewType
```

**`reset_handler`** is the part of `unregister_type` that is the same for both tables:

```python
try:
    original = builtin.get(key)
    current = live.get(key)
except TypeError:                                  # an unhashable key was never registered
    return False

if original is not None:                           # a built-in exists — restore it, do not delete it
    live[key] = original
    return current is not original

return live.pop(key, None) is not None             # otherwise it is purely a registration — remove it
```

**The built-in readers** are small wrappers that check the kind of data once per group, before the
class is called (a wrong kind raises a plain `TypeError`, which `deserialize` turns into a card):

```python
def _from_text(build):                             # dates, PurePath, UUID, network addresses, base64 bytes
    def handler(data, target):
        if not isinstance(data, str):
            raise TypeError(f"expected text, got {type(data).__name__}")
        return build(data, target)
    return handler

# the same idea: `_from_text_or_int` (Decimal, Fraction — no float, no bool), `_from_number` (timedelta — no bool)

BUILTIN_FROM_HANDLERS = MappingProxyType({
    datetime: _from_text(lambda data, target: target.fromisoformat(data)),
    PurePath: _from_text(lambda data, target: target(data)),           # the class you ask for builds itself
    bytes:    _from_text(lambda data, target: target(base64.b64decode(data, validate=True))),
    Enum:     lambda data, target: target(data),                       # open on purpose: any JSON kind
    ...
})
```

Every handler calls the **annotation it receives** (`target(data)`, `target.fromisoformat(data)`),
never a hard-coded class — asking for a `Path` gives a `Path`, asking for a `PurePosixPath` gives a
`PurePosixPath`, both through the same `PurePath` entry.

[▲ Back to top](#-table-of-contents)

---

### Errors of this package

Every error is a [`ParamError`](https://pypi.org/project/simplibs-exception/) card; the names start
with `SERIALIZE_REGISTER_`. They are raised by `register_type`, before anything is stored.

| Error name                                | Wraps        | Raised by       | When                                                         |
|-------------------------------------------|--------------|-----------------|--------------------------------------------------------------|
| `SERIALIZE_REGISTER_NO_HANDLER`           | `ValueError` | `register_type` | Neither `to_func` nor `from_func` is given                   |
| `SERIALIZE_REGISTER_NOT_A_TYPE`           | `TypeError`  | `register_type` | `type_` is not a class, a subscripted annotation or a `NewType` |
| `SERIALIZE_REGISTER_UNHASHABLE_TYPE`      | `TypeError`  | `register_type` | `type_` is not hashable, so it cannot be a key               |
| `SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS`  | `TypeError`  | `register_type` | `to_func` is given for something that is not a class         |

What a registered handler does **at conversion time** is reported by the other packages:
`SERIALIZE_HANDLER_FAILED` ([`serialize`](README_SERIALIZE_SERIALIZER.md#errors-of-this-package))
and `DESERIALIZE_BUILD_FAILED` ([`deserialize`](README_SERIALIZE_DESERIALIZER.md#errors-of-this-package)).

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicregistry--teach-it-your-types)
