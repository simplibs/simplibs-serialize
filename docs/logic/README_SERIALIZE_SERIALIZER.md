# 📤 `logic/serializer` — The Way Out

The `serializer` package turns **any Python object into a structure `json.dumps` accepts** —
nothing but `None`, `bool`, `int`, `float`, `str`, `list` and `dict`. It does no I/O and writes no
text: it **returns a structure**, and [`to_json` and `dump_json_file`](README_SERIALIZE_JSON_IO.md)
write it. Besides the conversion itself it holds the one question you ask before it: *would this
work at all?*

```python
from simplibs.serialize import serialize, is_serializable

data = serialize({"when": date(2024, 1, 2), "tags": {"b", "a"}})
# -> {"when": "2024-01-02", "tags": ["a", "b"]}
```

Both functions are wrapped in `@validate_call`, so a wrong type of `default` or `allow_nan` is
rejected with a `ValidationError` before the body runs. Each has an
[action counterpart](../README_SERIALIZE_ACTIONS.md) for pipelines (`Serialize`).

## A note on "an unknown object is an error"

`serialize` never guesses. An object nobody knows how to convert is **not** written as
`str(obj)` and **not** as its `__dict__` — a file full of `"<Foo object at 0x7f...>"` can never be
read back, and the mistake would surface months later, in the reader. The explicit way to ask
for a fallback is `default=`, exactly like `json.dumps(default=...)`: it is called only for what
nothing else knows, and it never overrides a rule the library already has.

## A note on the order of decisions

Every value that is not an exact primitive goes through the same ordered list. The order is
written down in one place (`encode_structure`) and it is not accidental:

| # | Kind of value                                         | Becomes                                     |
|---|-------------------------------------------------------|---------------------------------------------|
| 1 | A type with a registered or built-in handler (`date`, `UUID`, `Enum`, your own) | the handler's result, converted again |
| 2 | A subclass of `str`, `int` or `float`                 | the plain value inside it                   |
| 3 | A `NamedTuple`                                        | a `dict` of its fields                      |
| 4 | Any mapping (`dict`, `OrderedDict`, `MappingProxyType`, …) | a `dict` with text keys                |
| 5 | A dataclass **instance**                              | a `dict` of its fields                      |
| 6 | Any sequence, set, or `dict.values()`                 | a `list`                                    |
| 7 | Anything else, when `default=` is given               | `default(obj)`, converted again             |
| 8 | Anything else                                         | `SerializationError` (`SERIALIZE_UNSUPPORTED_TYPE`) |

Why this order: a handler **you registered wins** over the general rule for the `dict` or
`list` your class happens to derive from; a primitive subclass comes before the containers
because a `str` is a `Sequence` and must not turn into a list of characters; a `NamedTuple` comes
before sequences because it *is* a tuple, but its names are data; and `default` comes last because
it is for what is **unknown**, not an override.

## A note on keys, sets and the reader's eyes

* **Keys are always text.** `1` → `"1"`, `1.5` → `"1.5"`, `True` → `"true"`, `None` → `"null"` —
  the same texts `json.dumps` writes; an `Enum`, a `date` or a `UUID` key gives the text of its
  value. A tuple key has no honest text form and is an error; so are two keys that become the
  same text (`{1: "a", "1": "b"}` would silently lose one).
* **Sets are written in a fixed order.** The order of a `set` of strings changes with every
  interpreter start, so the same data would produce a different file every time. Items that can be
  compared are sorted the natural way (`2` before `10`), the rest by their JSON text.
* **Dataclass fields keep their declaration order**, each under its name in the data
  ([`serialized_field`](README_SERIALIZE_FIELDS.md) can give it an alias or leave it out).
* **Every error says where.** The location is written as `$.servers[2].host`; a key with a dot,
  a space or a dash is quoted: `$['user-name']`.

## A note on circles and shared references

A list that contains itself is a **circular reference** and an error. The same list used in two
places side by side is fine: the library only remembers the objects it is *currently inside*
(from the root down to the present value) and forgets each one when it leaves it. A handler that
returns its own argument is a circle too, and is caught the same way.

## A note on errors

| Situation                                                       | Exception            |
|-----------------------------------------------------------------|----------------------|
| An unsupported type, a circle, `nan`/`inf`, a duplicate or unsupported key, a failing handler, endless nesting | `SerializationError` |
| A dataclass field with invalid `metadata` options               | `ParamError`         |

`SerializationError` is a [`ConversionError`](https://pypi.org/project/simplibs-exception/); all
the library's errors share the root `SerializeError`, so one `except SerializeError` catches
everything. Every one is a structured card with the location in its `label`.

---

## 🧭 Table of Contents

* [`serialize`](#serialize)
* [`is_serializable`](#is_serializable)
* [The helpers behind them](#the-helpers-behind-them)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../../README.md#-logicserializer--the-way-out)

---

### `serialize`

Converts a Python object into a structure of plain JSON-compatible values — the function you reach
for whenever something has to leave your program as data.

**Parameters:**

* `obj` (*Any*): The value to convert.
* `default` (*ToHandler | None*, keyword-only, default `None`): Called as `default(obj)` for an object nothing else knows how to convert. Its result is converted again. Without it such an object is an error.
* `allow_nan` (*bool*, keyword-only, default `False`): If `True`, `nan` and `inf` pass through. They are not valid JSON, so by default they are an error.

**Returns:**

* `Any`: A structure made only of `None`, `bool`, `int`, `float`, `str`, `list` and `dict` — always something `json.dumps` accepts.

**Raises:**

* `SerializationError` (`SERIALIZE_UNSUPPORTED_TYPE`): No serializer is known for the type and there is no `default`.
* `SerializationError` (`SERIALIZE_CIRCULAR_REFERENCE`): An object contains itself.
* `SerializationError` (`SERIALIZE_NON_FINITE_NUMBER`): A `nan` or `inf` and `allow_nan=False`.
* `SerializationError` (`SERIALIZE_DUPLICATE_KEY`): Two entries would be written under one key.
* `SerializationError` (`SERIALIZE_UNSUPPORTED_KEY`): A key has no text form (a tuple, for example).
* `SerializationError` (`SERIALIZE_HANDLER_FAILED`): A handler (or `default`) raised an exception of its own.
* `SerializationError` (`SERIALIZE_TOO_DEEP`): The nesting never ends or exceeds the interpreter's limit.
* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options.

**Example usage:**

```python
serialize({"a": 1, "b": [True, None]})      # -> {"a": 1, "b": [True, None]}
serialize((1, 2, 3))                        # -> [1, 2, 3]
serialize({3, 1, 2})                        # -> [1, 2, 3]
serialize({1: "a", "1": "b"})              # -> raises: SERIALIZE_DUPLICATE_KEY (both are "1")
serialize({(1, 2): "a"})                    # -> raises: SERIALIZE_UNSUPPORTED_KEY (a tuple key)

serialize({"when": date(2024, 1, 2)})       # -> {"when": "2024-01-02"}
serialize(Color.RED)                        # -> "red"     (an Enum gives its value)

serialize(float("nan"))                     # -> raises: SERIALIZE_NON_FINITE_NUMBER
serialize(float("nan"), allow_nan=True)     # -> nan
serialize(object())                         # -> raises: SERIALIZE_UNSUPPORTED_TYPE
serialize(object(), default=lambda o: "?")  # -> "?"
```

**A dataclass** becomes a `dict` in declaration order; an alias renames a field and
`exclude=True` leaves it out:

```python
@dataclass
class User:
    name: str
    user_name: str = serialized_field(alias="userName", default="")
    token: str = serialized_field(exclude=True, default="")

serialize(User("Eva", "eva", "secret"))    # -> {"name": "Eva", "userName": "eva"}
```

**Where it went wrong.** A card names the exact spot — and it uses the name **in the data**, because
that is what the reader of the file sees:

```python
serialize({"servers": [{"host": "a"}, {"host": object()}]})
# -> raises: SERIALIZE_UNSUPPORTED_TYPE  at  $.servers[1].host
```

**Why `default=` is a last resort.** It sees only what nothing else recognised, so it can never
break a rule the library already has. Its result is converted again — a handler may return a
`dict` that holds dates or an enum member, and it stays one line long.

**Under the hood:**
```python
# 1. Everything one call needs is carried in one object
context = SerializeContext(
    default=default,
    allow_nan=allow_nan,
    encode_value=encode_value,
)

# 2. Convert from the root; a loop that never ends becomes a readable card
try:
    return context.encode(obj, ())
except RecursionError:
    raise_too_deep_error()
```

> 💡 `RecursionError` is caught **only here, at the top**: a nesting deeper than the interpreter
> allows cannot be located exactly, but it can be named. Everything else carries its own location.

[▲ Back to top](#-table-of-contents)

---

### `is_serializable`

Asks `serialize` whether it would succeed — before a file is touched or a message is sent, and
without a `try/except` around the real call.

**Parameters:**

* `obj` (*Any*): The value to try.
* `default` (*ToHandler | None*, keyword-only, default `None`): The same fallback `serialize` takes.
* `allow_nan` (*bool*, keyword-only, default `False`): The same switch `serialize` takes.

**Returns:**

* `bool`: `True` if the object can be serialized, `False` if `serialize` would raise `SerializationError`.

**Raises:**

* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options — see the note below.

**Example usage:**

```python
is_serializable({"a": [1, 2, 3]})              # -> True
is_serializable(object())                      # -> False
is_serializable(object(), default=str)         # -> True      (the fallback takes it)
is_serializable(float("nan"))                  # -> False
is_serializable(float("nan"), allow_nan=True)  # -> True
```

**A real run, not a guess.** The function performs the full conversion and throws the result
away. A separate "can it be done" walk would have to repeat every decision `serialize` makes and
would drift from it with the first change; the price is one extra pass.

**Only `SerializationError` means "no".** A broken `metadata` option on a dataclass field is a bug
in the code that **declares** the class, not a property of the value — so the `ParamError` passes
through instead of being turned into `False`.

**Under the hood:**
```python
# 1. Run the real thing — a prediction could disagree with it
try:
    serialize(obj, default=default, allow_nan=allow_nan)
except SerializationError:
    return False

# 2. Nothing went wrong
return True
```

> 💡 For a value you are going to serialize anyway, just call `serialize` and handle the error —
> `is_serializable` pays for the conversion twice. It is for the moment **before** something
> irreversible, and as the building block of the [`IsSerializable` rule](../README_SERIALIZE_RULES.md).

[▲ Back to top](#-table-of-contents)

---

### The helpers behind them

Small internal helpers (not exported) carry the work. Every encoder is an independent file: it
recurses through `context.encode(value, location)` and never imports the dispatcher, so there is
no circular import and each one can be tested with a fake context.

| Helper                                   | What it does                                                                    | Used by               |
|------------------------------------------|---------------------------------------------------------------------------------|-----------------------|
| `SerializeContext`                       | Everything one call carries: `default`, `allow_nan`, the dispatcher, and the objects currently being converted. | every encoder |
| `encode_value(obj, location, context)`   | The door of every value: `None` and exact primitives leave at once; the rest is guarded against circles. | `serialize`, the context |
| `encode_structure(obj, location, context)` | Chooses the encoder — the ordered list from the table above.                  | `encode_value`        |
| `encode_items(obj, location, context)`   | A sequence or a set to a `list`; a set in a fixed order.                        | `encode_structure`    |
| `encode_mapping(obj, location, context)` | Any mapping to a `dict` with text keys; refuses two keys with one text.         | `encode_structure`    |
| `encode_mapping_key(key, location, context)` | One key to the text a JSON object needs.                                    | `encode_mapping`      |
| `encode_dataclass(obj, location, context)` | A dataclass instance to a `dict` of its fields (alias, exclusion).            | `encode_structure`    |
| `encode_with_handler(handler, obj, location, context)` | One handler call: call, wrap a failure, convert the result.        | `encode_structure`    |
| `sort_items(items)`                      | Gives the converted items of a set a fixed order.                               | `encode_items`        |
| `to_primitive(obj)`                      | The plain `str`, `int` or `float` inside a subclass of one.                     | `encode_structure`    |

**`encode_value`** is the hot path — most values in real data are plain primitives and leave in a
few comparisons without ever reaching a lookup. The type check is **exact** (`type(obj) in
JSON_PRIMITIVES`), so a subclass takes the structure path, where a registered handler (an `Enum`)
is found before anything treats it as plain text. It is also the **only** place that guards
against circles: one place adds an id on the way in and removes it on the way out, so no encoder
has to remember to:

```python
if obj is None:
    return None

kind = type(obj)
if kind in JSON_PRIMITIVES:                           # only a float can still be wrong
    if kind is float and not context.allow_nan and not math.isfinite(obj):
        raise_non_finite_number_error(location, obj)
    return obj

identity = id(obj)
if identity in context.ancestors:                     # already being converted further up
    raise_circular_reference_error(location, obj)

context.ancestors.add(identity)
try:
    return encode_structure(obj, location, context)
finally:
    context.ancestors.discard(identity)               # the same object side by side is fine
```

**`encode_structure`** is the ordered list from the table — the one place where the order of
decisions is written down:

```python
handler = find_to_handler(type(obj))                  # through the class hierarchy
if handler is not None:
    return encode_with_handler(handler, obj, location, context)

if isinstance(obj, JSON_PRIMITIVES):                  # str / int / float subclass
    return context.encode(to_primitive(obj), location)

if is_named_tuple(obj):                               # before it is taken for a plain tuple
    return context.encode(obj._asdict(), location)

if isinstance(obj, Mapping):
    return encode_mapping(obj, location, context)

if dataclasses.is_dataclass(obj) and not isinstance(obj, type):   # the class itself is not data
    return encode_dataclass(obj, location, context)

if isinstance(obj, (Sequence, Set, ValuesView)):
    return encode_items(obj, location, context)

if context.default is not None:                       # the caller's fallback, for the unknown only
    return encode_with_handler(context.default, obj, location, context)

raise_unsupported_type_error(location, obj)
```

**`encode_items`** converts every item first and sorts afterwards, so a set of `Color.RED` and
`Color.BLUE` is ordered by **what is written for them**. An index in an error location is the
item's position in the set's own iteration order — the only order there is to point at:

```python
items = [
    context.encode(item, (*location, index))
    for index, item in enumerate(obj)
]

if isinstance(obj, Set):                              # a set has no order of its own, so it is given one
    return sort_items(items)
return items                                          # a sequence keeps the order it has
```

**`sort_items`** has two ways and neither depends on anything random:

```python
try:
    return sorted(items)                              # numbers by size, text alphabetically — 2 before 10
except TypeError:
    pass
return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))   # a mix: None next to a number, dicts
```

**`encode_mapping`** keeps insertion order and refuses the silent loss of an entry:

```python
result: dict[str, Any] = {}
for key, value in obj.items():
    text = encode_mapping_key(key, location, context)
    if text in result:                                # `{1: "a", "1": "b"}` would lose one of the two
        raise_duplicate_key_error(location, text)
    result[text] = context.encode(value, (*location, text))
return result
```

**`encode_mapping_key`** follows the rules of `json.dumps`, not `str(key)` — a plain `str()` would
write `"Color.RED"` for an enum and `"None"` for `None`, texts nobody could turn back into the key:

```python
if type(key) is str:
    return key

encoded = context.encode(key, location)               # an enum gives its value, a date its ISO text
if isinstance(encoded, str):
    return encoded
if encoded is None:
    return "null"
if isinstance(encoded, bool):                         # bool before int
    return "true" if encoded else "false"
if isinstance(encoded, (int, float)):
    return repr(encoded)

raise_unsupported_key_error(location, key)            # a list or a dict (a tuple, for example)
```

**`encode_dataclass`** writes fields in declaration order under the name they have in the data.
Fields with `init=False` **are** written — they are part of the object's state; the way back knows
them and does not require them:

```python
result: dict[str, Any] = {}
for field in dataclasses.fields(obj):
    name, exclude = get_field_options(field)
    if exclude:
        continue
    if name in result:                                # two fields with one alias would lose one
        raise_duplicate_key_error(location, name)
    result[name] = context.encode(getattr(obj, field.name), (*location, name))
return result
```

**`encode_with_handler`** serves the registered handlers and `default` alike. The result is
converted **again**, so a `to_func` can stay one line long
(`lambda p: {"when": p.when, "who": p.who}`):

```python
try:
    result = handler(obj)
except (SerializeError, RecursionError):              # already a card with a location / the top handles it
    raise
except Exception as caught:
    raise_handler_failed_error(location, obj, caught) # the original is attached as the cause

return context.encode(result, location)
```

**`to_primitive`** returns the stored value of a `class Name(str)` or `class Port(int)` — not
`str(obj)`, which would call the subclass's own `__str__` and may return something else entirely:

```python
if isinstance(obj, str):
    return str.__str__(obj)
if isinstance(obj, int):
    return int.__int__(obj)
return float.__float__(obj)
```

An enum member never gets here — its handler is found first, so a `class Color(str, Enum)` is
written as its value and not as the text of its name.

**`SerializeContext`** is a `slots` dataclass made anew for every call — nothing is shared
between calls or threads. It cannot be frozen, because `ancestors` changes during the walk.

[▲ Back to top](#-table-of-contents)

---

### Errors of this package

Every error is a structured card ([`simplibs-exception`](https://pypi.org/project/simplibs-exception/)); the
names start with `SERIALIZE_`. The `label` of a card is the location (`$.servers[2].host`), the
`value` is the offending object.

| Error name                      | Class                | Wraps        | Raised by           | When                                                         |
|---------------------------------|----------------------|--------------|---------------------|--------------------------------------------------------------|
| `SERIALIZE_UNSUPPORTED_TYPE`    | `SerializationError` | `TypeError`  | `encode_structure`  | No handler, no known kind, and no `default`                  |
| `SERIALIZE_UNSUPPORTED_KEY`     | `SerializationError` | `TypeError`  | `encode_mapping_key`| A key is converted to a list or a dict (a tuple)             |
| `SERIALIZE_CIRCULAR_REFERENCE`  | `SerializationError` | `ValueError` | `encode_value`      | An object is met again while it is being converted           |
| `SERIALIZE_NON_FINITE_NUMBER`   | `SerializationError` | `ValueError` | `encode_value`      | A `nan` or `inf` float and `allow_nan=False`                 |
| `SERIALIZE_DUPLICATE_KEY`       | `SerializationError` | `ValueError` | `encode_mapping`, `encode_dataclass` | Two keys (or aliases) become the same text |
| `SERIALIZE_HANDLER_FAILED`      | `SerializationError` | `ValueError` | `encode_with_handler` | A handler or `default` raised an exception (kept as cause) |
| `SERIALIZE_TOO_DEEP`            | `SerializationError` | `ValueError` | `serialize`         | `RecursionError` — nesting beyond the interpreter's limit    |
| `SERIALIZE_INVALID_FIELD_OPTIONS` | `ParamError`       | `ValueError` | `encode_dataclass` (via `get_field_options`) | A field's `metadata` options are broken |

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicserializer--the-way-out)
