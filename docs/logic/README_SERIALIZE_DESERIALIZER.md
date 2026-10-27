# 📥 `logic/deserializer` — The Way Back

The `deserializer` package builds **a value of a given type from serialized data** — the mirror
of [`serialize`](README_SERIALIZE_SERIALIZER.md). You hand it the data (from `serialize`, from
`json.loads`, from a file) and an **annotation**, and you get back a dataclass, a `list[date]`, a
`dict[Color, Point]` — or a card that says exactly where and why the data does not fit. Besides
the conversion itself it holds the one question you ask before it: *would this fit at all?*

```python
from simplibs.serialize import deserialize, is_deserializable

point = deserialize({"x": 1, "y": 2}, Point)           # -> Point(x=1, y=2)
dates = deserialize(["2024-01-02"], list[date])        # -> [date(2024, 1, 2)]
```

Both functions are wrapped in `@validate_call`, so a wrong type of `strict` is rejected with a
`ValidationError` before the body runs. Each has an
[action counterpart](../README_SERIALIZE_ACTIONS.md) for pipelines (`Deserialize`).

## A note on "the annotation is the schema"

Nothing is guessed from the data. With `Point | Circle` the data alone cannot say which one is
meant; with `dict[str, int]` it cannot say the values are ints. The caller knows, so the caller
says — and every part of the data is **checked** against what the annotation asks for. A typo in a
config file stops at the door instead of travelling on into the program.

## A note on what can be built

| Annotation                                                        | Data it reads                          | Result                               |
|-------------------------------------------------------------------|----------------------------------------|--------------------------------------|
| `str`, `int`, `float`, `bool`, `None`, `Any` (and subclasses of the first four) | a matching JSON value    | the value (a subclass is constructed)|
| `list`, `set`, `frozenset`, `deque`, `Sequence`, `Collection`, `Iterable`, `Set`, `MutableSet` — bare or `list[int]` | a list | that container          |
| `tuple`, `tuple[int, ...]`, `tuple[int, str]`, `tuple[()]`        | a list                                 | a tuple (any length / fixed positions / empty) |
| `dict`, `OrderedDict`, `Mapping`, `MutableMapping` — bare or `dict[int, Point]` | an object               | that mapping, keys read back from text |
| `X \| Y`, `Union[X, Y]`, `Optional[X]`                            | anything one member fits               | the value built against that member  |
| `Annotated[T, rule, ...]`                                         | what `T` reads, **and** passes the rules | the value                          |
| `Literal["a", "b"]`                                               | one of the listed values               | that value (an enum member if listed)|
| a dataclass (also generic: `Box[int]`)                            | an object                              | an instance                          |
| a `NamedTuple`                                                    | an object (by name) or a list (by position) | an instance                    |
| a `TypedDict`                                                     | an object                              | a plain `dict`                       |
| any enum, and every type [built in or registered](README_SERIALIZE_REGISTRY.md) (`date`, `UUID`, `Path`, your own) | what its handler reads | the handler's result |
| `NewType`, a `type` alias, a `TypeVar`                            | what the name stands for               | built as the underlying annotation   |
| `Final[T]`, `Required[T]`, `NotRequired[T]`, `ReadOnly[T]`        | what `T` reads                         | the value (the wrapper changes nothing) |

Anything else — `Callable[..., int]`, for example — is a `DeserializationError`
(`DESERIALIZE_UNSUPPORTED_ANNOTATION`), not a silent pass-through.

## A note on being strict

* **Primitives are checked, not cast.** `int` accepts an int that is not a bool — not `1.0`, not
  `"1"`, not `True`. `float` accepts a float **or an int** (`1` is a fine `1.0`), never a bool.
  `bool` accepts only a bool; `str` only text. A silent cast would hide a mistake.
* **`None` is decided by the annotation, never by the data.** It is accepted for `None`, `Any`
  and for `Optional` / unions that contain it — and for nothing else.
* **`strict=True` (the default)** makes a dataclass, `NamedTuple` or `TypedDict` refuse keys it
  does not know. `strict=False` ignores them. Unknown keys are reported **together with** the
  missing ones — a typo (`"yy"` for `"y"`) shows up as both in one card.
* **A set may be smaller than its data.** `[1, 1]` read as `set[int]` is `{1}`: a set cannot hold
  two, and the library does not refuse data it could read.

## A note on unions

Every member is tried; a member that cannot build the data is simply not a candidate.

1. `None` is settled first: it belongs to the union, or the union has no answer.
2. `X | None` is **not a choice** — with `None` out of the way `X` is the only member, so its own
   error (with the deep location, `$.pt.x` and not just `$.pt`) is the one you see.
3. One candidate fits → that is the answer. None fits → one card at the union's location, with the
   failure that got **deepest** into the data attached as its cause.
4. Several fit → the member that is **exactly the data's own JSON type** wins: `5` fits `int | float`
   as `int`, `5.0` only as `float`, and `"2024-01-02"` fits `str | date` as the `str`.
5. A real tie is an error that lists the members that fit — `list[int] | list[str]` with `[]`.

> Mind `date | datetime`: the text `"2026-10-24"` is a valid `datetime` too (midnight), so both fit,
> neither is an exact primitive match, and the union is reported as ambiguous. Put the member the
> data really is in the annotation.

## A note on keys

JSON keys are text. The way back is driven by the **annotation**, not by the text: `"1"` is a `str`
for `dict[str, X]`, an `int` for `dict[int, X]`, and the member with value 1 for an `IntEnum`.
The forms a text can stand for are exactly the ones `serialize` writes — `"12"` and `"-3"` (not
`"012"` or `"+1"`), `"1.5"`, `"true"`, `"false"`, `"null"` — and the first one the annotation
accepts wins. Two texts that become one key (`"1"` and `"1.0"` for `dict[float, X]`) are an error
instead of a silently lost value.

## A note on dataclasses

* Every field is built against **its own type**, found under its name in the data — the alias, if
  [`serialized_field`](README_SERIALIZE_FIELDS.md) gave one. Forward references and string
  annotations are resolved, and `Annotated` is kept so that its rules still run.
* A field with a default (or a factory) may be missing from the data. Without one it is reported
  as missing.
* An **excluded** field is never in the data; it must come from its default — without one it can
  never be built, and the card says so.
* An `init=False` field **may** be in the data (`serialize` writes it) but is never passed to the
  constructor.
* A generic dataclass works: `Box[int]` fills `T` with `int`; a bare `Box` leaves `T` to its bound,
  or `Any`.
* A constructor that refuses the values (`__post_init__`, `validate_dataclass`) ends as a card with
  the location; its own exception is the cause.

## A note on rules

`simplibs-types` builds its types as `Annotated[int, rule]`. Dropping everything after the first
argument would let an `int_port` read from a file accept `-5`. So every **rule** in the metadata —
a `Rule`, or a plain predicate function — is checked, and a failed one is a
`DeserializationError` with the location and what the rule requires. Anything else in the
metadata (a docstring, a marker class) belongs to somebody else and is skipped.

## A note on errors

| Situation                                                       | Exception              |
|-----------------------------------------------------------------|------------------------|
| The data does not fit the annotation, or the annotation is not supported | `DeserializationError` |
| A dataclass field with invalid `metadata` options               | `ParamError`           |

`DeserializationError` is a [`ConversionError`](https://pypi.org/project/simplibs-exception/); all
the library's errors share the root `SerializeError`. The `label` of every card is the location
of the value, written as `$.servers[2].port`.

---

## 🧭 Table of Contents

* [`deserialize`](#deserialize)
* [`is_deserializable`](#is_deserializable)
* [The helpers behind them](#the-helpers-behind-them)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../../README.md#-logicdeserializer--the-way-back)

---

### `deserialize`

Builds a value of the given type from serialized data — the function you reach for whenever data
comes **into** your program.

**Parameters:**

* `data` (*Any*): The serialized data — from `serialize`, or any JSON-decoded structure.
* `annotation` (*TargetType*): What to build: a class, a dataclass, `list[int]`, `dict[str, Point]`, `int | None`, `Literal["a", "b"]`, an enum, …
* `strict` (*bool*, keyword-only, default `True`): If `True`, a dataclass, `NamedTuple` or `TypedDict` refuses data with keys it does not know. If `False`, those keys are ignored.

**Returns:**

* *Any*: A value of the requested type — for `annotation: type[T]` the type checkers see a `T`.

**Raises:**

* `DeserializationError` (`DESERIALIZE_WRONG_TYPE`): The data is not the kind the annotation asks for.
* `DeserializationError` (`DESERIALIZE_MISSING_FIELD`, `DESERIALIZE_UNKNOWN_FIELD`): A required field is absent / `strict` meets a key it does not know.
* `DeserializationError` (`DESERIALIZE_UNION_NO_MATCH`, `DESERIALIZE_UNION_AMBIGUOUS`): No member of a union fits / more than one fits equally well.
* `DeserializationError` (`DESERIALIZE_LITERAL_MISMATCH`, `DESERIALIZE_RULE_FAILED`): The data is not a listed value / breaks a rule of `Annotated`.
* `DeserializationError` (`DESERIALIZE_WRONG_LENGTH`, `DESERIALIZE_INVALID_KEY`, `DESERIALIZE_KEY_COLLISION`): A tuple or `NamedTuple` has the wrong length; a key cannot be read back; two keys become one.
* `DeserializationError` (`DESERIALIZE_BUILD_FAILED`): A constructor or handler refused the data (its exception is the cause).
* `DeserializationError` (`DESERIALIZE_UNSUPPORTED_ANNOTATION`): The annotation is not one the library can build.
* `DeserializationError` (`DESERIALIZE_DATA_TOO_DEEP`): The data is nested beyond the interpreter's limit.
* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options.

**Example usage:**

```python
deserialize([1, 2, 3], list[int])                  # -> [1, 2, 3]
deserialize([1, 2, 2], set[int])                   # -> {1, 2}
deserialize({"1": "a"}, dict[int, str])            # -> {1: "a"}
deserialize("red", Color)                          # -> Color.RED
deserialize("debug", Literal["debug", "info"])     # -> "debug"

deserialize(1, float)                              # -> 1.0
deserialize("5", int)                              # -> raises: DESERIALIZE_WRONG_TYPE (text, not an int)
deserialize(True, int)                             # -> raises: DESERIALIZE_WRONG_TYPE (a bool is not an int)
deserialize(None, int)                             # -> raises: DESERIALIZE_WRONG_TYPE
deserialize(None, int | None)                      # -> None
```

**A dataclass** is built field by field; the location of a failure is the name in the data:

```python
@dataclass
class Server:
    host: str
    port: Annotated[int, lambda n: 0 < n < 65536]

deserialize({"host": "a", "port": 80}, Server)         # -> Server(host="a", port=80)
deserialize({"host": "a", "port": -5}, Server)         # -> raises: DESERIALIZE_RULE_FAILED at $.port
deserialize({"host": "a"}, Server)                     # -> raises: DESERIALIZE_MISSING_FIELD (port)
deserialize({"host": "a", "port": 80, "x": 1}, Server)               # -> raises: DESERIALIZE_UNKNOWN_FIELD (x)
deserialize({"host": "a", "port": 80, "x": 1}, Server, strict=False) # -> Server(host="a", port=80)

deserialize({"servers": [{"host": "a", "port": 80}, {"host": "b", "port": "x"}]}, Config)
# -> raises: DESERIALIZE_WRONG_TYPE  at  $.servers[1].port
```

**A `NamedTuple` and a union:**

```python
class Point(NamedTuple):
    x: int
    y: int = 0

deserialize({"x": 1, "y": 2}, Point)      # -> Point(x=1, y=2)    (the way `serialize` writes it)
deserialize([1, 2], Point)                # -> Point(x=1, y=2)    (a list, by position)
deserialize([1], Point)                   # -> Point(x=1, y=0)    (a default may be missing at the end)

deserialize(5, int | float)               # -> 5                   (exactly an int)
deserialize(5.0, int | float)             # -> 5.0
deserialize([], list[int] | list[str])    # -> raises: DESERIALIZE_UNION_AMBIGUOUS
```

**Why the annotation is checked, not trusted.** The easy version — return the data untouched
whenever the annotation is a primitive — would make `deserialize("abc", int)` return `"abc"`. The
price of being strict is one clear card per mistake; the reward is that everything that comes out
of `deserialize` **is** what its annotation says.

**Under the hood:**
```python
# 1. Everything one call needs is carried in one object
context = DeserializeContext(strict=strict, build_value=build_value)

# 2. Build from the root; data nested beyond the interpreter's limit gets a card
try:
    return context.build(data, annotation, ())
except RecursionError:
    raise_data_too_deep_error()
```

> 💡 There is no cycle to detect when reading: data is finite and the annotation does not change
> while it is read. That is why the context holds only `strict` and the way to recurse.

[▲ Back to top](#-table-of-contents)

---

### `is_deserializable`

Asks `deserialize` whether it would succeed — to check a configuration or a message against a type
without a `try/except` around the real call.

**Parameters:**

* `data` (*Any*): The serialized data.
* `annotation` (*TargetType*): The type to build.
* `strict` (*bool*, keyword-only, default `True`): The same switch `deserialize` takes.

**Returns:**

* `bool`: `True` if the data can be built into the annotation, `False` if `deserialize` would raise `DeserializationError`.

**Raises:**

* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options — see the note below.

**Example usage:**

```python
is_deserializable({"x": 1, "y": 2}, Point)                 # -> True
is_deserializable({"x": 1}, Point)                         # -> False   (y missing)
is_deserializable({"x": 1, "y": 2, "z": 3}, Point)         # -> False   (strict: z is unknown)
is_deserializable({"x": 1, "y": 2, "z": 3}, Point, strict=False)   # -> True
is_deserializable("5", int)                                # -> False
```

**A real run, not a guess.** Like [`is_serializable`](README_SERIALIZE_SERIALIZER.md#is_serializable)
it performs the full build and discards the result, so it cannot disagree with `deserialize`.

**Only `DeserializationError` means "no".** A broken `metadata` option is a bug in the class
declaration, not a property of the data, and the `ParamError` passes through.

**Under the hood:**
```python
# 1. Run the real thing — a prediction could disagree with it
try:
    deserialize(data, annotation, strict=strict)
except DeserializationError:
    return False

# 2. Nothing went wrong
return True
```

> 💡 An annotation the library cannot build is a `DeserializationError` as well, so it gives
> `False` — not an exception. If you are not sure the annotation itself is supported, call
> `deserialize` once with data you know is good.

[▲ Back to top](#-table-of-contents)

---

### The helpers behind them

Small internal helpers (not exported) carry the work. Every builder is an independent file: it
recurses through `context.build(data, annotation, location)` and never imports the dispatcher, so
there is no circular import and each one can be tested with a fake context.

| Builder                                   | What it builds                                                          |
|-------------------------------------------|-------------------------------------------------------------------------|
| `build_value`                             | The dispatcher: chooses the builder — the ordered list below.          |
| `build_primitive_value`                   | `str`, `int`, `float`, `bool` and their subclasses — checked.          |
| `build_elements_value`                    | `list`, `set`, `frozenset`, `deque` and the abstract collections.      |
| `build_tuple_value`                       | A tuple: bare, `tuple[T, ...]`, `tuple[A, B]`, `tuple[()]`.            |
| `build_mapping_value`, `build_mapping_key`| A mapping; each key read back from its text.                           |
| `build_union_value`                       | `X \| Y`, `Union`, `Optional` — which member is meant.                 |
| `build_annotated_value`                   | `Annotated[T, rule, ...]` — build `T`, then check every rule.          |
| `build_literal_value`                     | `Literal[...]` — same type and equal value.                            |
| `build_dataclass_value`                   | A dataclass, each field against its own type.                          |
| `build_named_tuple_value`                 | A `NamedTuple` from an object or a list.                               |
| `build_typed_dict_value`                  | A `TypedDict` — a plain dict with a schema.                            |
| `build_alias_value`, `build_qualified_value` | `NewType` / `type` alias / `TypeVar`; `Final` / `Required` / …      |
| `build_with_handler`                      | One registered `from_func` call, with its failure wrapped.             |

| Small helper                              | What it does                                                                 | Used by                    |
|-------------------------------------------|------------------------------------------------------------------------------|----------------------------|
| `DeserializeContext`                      | `strict` and `build`, the way every builder recurses.                        | every builder              |
| `BUILDER_TABLE`                           | Origin of an annotation (`list` for `list[int]`) → its builder.              | `build_value`              |
| `ELEMENT_FACTORIES`, `MAPPING_FACTORIES`  | Origin → how the built items / entries become the container.                 | `build_elements_value`, `build_mapping_value` |
| `resolve_type_hints(annotation)`          | The real type of every field, forward references and type variables resolved. | dataclass, `NamedTuple`, `TypedDict` builders |
| `has_default(field)`                      | Can the field be left out of the constructor call.                           | `build_dataclass_value`    |
| `key_candidates(text)`                    | The forms a key text can stand for, most literal first.                      | `build_mapping_key`        |
| `closest_failure(failures)`               | The failure of the union member that got deepest into the data.              | `build_union_value`        |
| `is_exact_type_match(data, member)`       | Is the data exactly the primitive the union member names.                    | `build_union_value`        |
| `is_rule_like(item)`                      | Is an item of `Annotated` metadata a rule or a predicate.                    | `build_annotated_value`    |
| `is_alias_annotation(annotation)`         | Is it a `NewType`, a `type` alias or a `TypeVar`.                            | `build_value`              |

**`build_value`** is the one place where the order of decisions is written down. A handler comes
first, so whatever you register for a class, a `NewType` or an exact annotation such as `list[int]`
wins over the general rule; primitives come before the table (an `int` must not become a
"container"); the table comes before the classes (`list[Point]` is a list first). Enums need no
branch of their own — the `Enum` handler is found along the class hierarchy:

```python
if annotation is Any or annotation is object:                  # 1. anything goes
    return data

handler = find_from_handler(annotation)                        # 2. enums, dates, paths, UUIDs, your types
if handler is not None:
    if data is None and isinstance(annotation, type) and get_origin(annotation) is None:
        raise_wrong_type_error(location, annotation, data)     #    a class never receives None
    return build_with_handler(handler, data, annotation, location)

if annotation is None or annotation is NoneType:               # 3. None — decided by the annotation
    if data is not None:
        raise_wrong_type_error(location, annotation, data)
    return None

if (isinstance(annotation, type) and get_origin(annotation) is None
        and issubclass(annotation, JSON_PRIMITIVES)):          # 4. str, int, float, bool
    return build_primitive_value(data, annotation, location)

origin = get_origin(annotation)                                # 5. containers, unions, Annotated, Literal
builder = BUILDER_TABLE.get(annotation if origin is None else origin)
if builder is not None:
    return builder(data, annotation, location, context)

if is_alias_annotation(annotation):                            # 6. NewType, `type` alias, TypeVar
    return build_alias_value(data, annotation, location, context)

cls = annotation if origin is None else origin                 # 7. classes with a structure of their own
if isinstance(cls, type):
    if dataclasses.is_dataclass(cls):
        return build_dataclass_value(data, annotation, location, context)
    if is_typeddict(cls):
        return build_typed_dict_value(data, annotation, location, context)
    if is_named_tuple_class(cls):
        return build_named_tuple_value(data, annotation, location, context)

raise_unsupported_annotation_error(location, annotation)       # 8. nothing recognized
```

**`BUILDER_TABLE`** is one read-only table instead of a ladder of `if`s. It is keyed by
`get_origin(annotation)` (`list[int]` → `list`) or, for an annotation without arguments, by the
annotation itself — so a bare `list` and `list[int]` reach the same builder, and the builder asks
for the arguments. Dataclasses, `NamedTuple`, `TypedDict`, `NewType` and `type` aliases have no
origin to key by, so `build_value` recognizes them by what they are.

**`build_primitive_value`** finds the primitive the annotation stands on, checks the data against
it, and only then builds a subclass — a constructor that refuses the value is a card, not a bare
exception:

```python
if base is bool:
    valid = isinstance(data, bool)
elif base is int:
    valid = isinstance(data, int) and not isinstance(data, bool)    # a bool is not an int
elif base is float:
    valid = isinstance(data, (int, float)) and not isinstance(data, bool)
else:
    valid = isinstance(data, str)
if not valid:
    raise_wrong_type_error(location, annotation, data)

value = float(data) if base is float else data       # an int may stand for a float; only that conversion is made
if annotation is base:
    return value
try:
    return annotation(value)                         # `class Port(int)` is built as `Port(value)`
except Exception as caught:
    raise_build_failed_error(location, annotation, caught)
```

**`build_elements_value` and `build_tuple_value`.** JSON has one array for all of these, and text
is not an array of characters. Items are built first, each with its index in the location; then
the container is made (a `set` can refuse an unhashable item — that is a card). `tuple` means
three different things, and only the arguments tell them apart:

```python
if not isinstance(data, (list, tuple)):
    raise_wrong_type_error(location, annotation, data)

if bare or (len(args) == 2 and args[1] is Ellipsis):    # `tuple` or `tuple[T, ...]` — any length
    ...
if len(data) != len(args):                              # `tuple[A, B, C]` — exactly that many
    raise_wrong_length_error(location, annotation, data, len(args), len(args))
```

`tuple[()]` has no arguments, like a bare `tuple`; only the missing origin tells them apart — it
means "must be empty". Origins that are not in `ELEMENT_FACTORIES` (`list`, `Sequence`,
`Iterable`, …) stay a `list`; the abstract `Set` becomes a `frozenset` (it promises no mutation),
`MutableSet` a `set`.

**`build_mapping_value` and `build_mapping_key`** build both halves of every entry — the key from
its text, the value from its data — and refuse two texts that become one key:

```python
for key, value in data.items():
    built_key = build_mapping_key(key, key_annotation, location, context)
    built_value = context.build(value, value_annotation, (*location, str(key)))
    if built_key in result:                                          # two texts, one key
        raise_key_collision_error(location, built_key, sources[built_key], key)
    result[built_key] = built_value
    sources[built_key] = key
```

`build_mapping_key` tries the forms `key_candidates` lists through the normal `build`, so enums,
dates, UUIDs, unions, `Annotated` rules and handlers all decide for themselves:

```python
if annotation is str or annotation is Any or annotation is object:   # text for text
    return key

candidates = key_candidates(key)                    # "1" -> ["1", 1, 1.0]   "true" -> ["true", True]
if annotation in (int, float, bool, NoneType):
    candidates = candidates[1:]                     # a number never accepts the text itself

for candidate in candidates:
    try:
        return context.build(candidate, annotation, location)
    except DeserializationError:
        continue
raise_invalid_key_error(location, annotation, key)
```

Only the **canonical** forms are candidates (`"012"` is not `12`: reading it so would make `"12"`
and `"012"` the same key, and writing it back would give a different file). `defaultdict` is
deliberately not in `MAPPING_FACTORIES` — it needs a default factory the annotation does not
carry; register a handler for it if one is needed.

**`build_union_value`** is the list from the note above:

```python
members = get_args(annotation)
if data is None:                                         # None is decided first
    if NoneType in members:
        return None
    raise_union_no_match_error(location, annotation, data)

candidates = [m for m in members if m is not NoneType]
if len(candidates) == 1:                                 # `Optional[X]` is no choice
    return context.build(data, candidates[0], location)

matches, failures = [], []
for member in candidates:                                # every member is tried
    try:
        matches.append((member, context.build(data, member, location)))
    except DeserializationError as caught:
        failures.append(caught)

if len(matches) == 1:
    return matches[0][1]
if not matches:                                          # the failure that got deepest becomes the cause
    raise_union_no_match_error(location, annotation, data, closest_failure(failures))

exact = [m for m in matches if is_exact_type_match(data, m[0])]
if len(exact) == 1:                                      # the member exactly the data's own type wins
    return exact[0][1]
raise_union_ambiguous_error(location, annotation, data, [m for m, _ in matches])
```

`closest_failure` reads the depth from the length of the failure's `label` (the formatted
location), so `$.pt.x` beats `$.pt`; on a tie the member listed first wins. `is_exact_type_match`
is a one-liner — only primitives have an "exact" type:

```python
return member in JSON_PRIMITIVES and type(data) is member      # `5` is an int, `True` is a bool and not an int
```

**`build_annotated_value`** builds the inner type first, then checks every rule — and a rule that
itself raises is a card, not a bare exception. A failed rule is a `DeserializationError` (not a
`ValidateError`), so one `except SerializeError` covers a bad file as a whole and a union can treat
it as "this member does not fit":

```python
inner, *metadata = get_args(annotation)
value = context.build(data, inner, location)

for item in metadata:
    if not is_rule_like(item):                           # somebody else's metadata
        continue
    try:
        passed = validate(value, item, return_bool=True)
    except Exception as caught:
        raise_build_failed_error(location, annotation, caught)
    if not passed:
        raise_rule_failed_error(location, item, value)
return value
```

`is_rule_like` accepts a `Rule`, or anything callable that is not a class (a marker type is
callable, but it is not a predicate).

**`build_literal_value`** demands the **same type** and an equal value — Python says
`True == 1` and `1.0 == 1`, and for data they mean different things. A listed enum member is
matched by its value, as it is written, and the member is returned:

```python
for allowed in get_args(annotation):
    candidate = allowed.value if isinstance(allowed, Enum) else allowed
    if type(data) is type(candidate) and data == candidate:
        return allowed
raise_literal_mismatch_error(location, annotation, data)       # the card lists the allowed values
```

**`build_dataclass_value`** is the longest builder, and the order inside it matters — unknown keys
are reported **first**, because they often explain a missing field:

```python
cls = annotation if get_origin(annotation) is None else get_origin(annotation)
hints = resolve_type_hints(annotation)               # forward references, type variables, Annotated kept

for field in dataclasses.fields(cls):
    name, exclude = get_field_options(field)
    if not field.init:                               # a derived field may be in the data, is never passed in
        known.add(name)
        continue
    if exclude:                                      # not data: it must come from its default
        if not has_default(field):
            missing.append(field.name)
        continue
    known.add(name)
    if name in data:
        kwargs[field.name] = context.build(data[name], hints.get(field.name, Any), (*location, name))
    elif not has_default(field):
        missing.append(name)

if context.strict:
    unknown = sorted((key for key in data if key not in known), key=str)
    if unknown:
        raise_unknown_field_error(location, annotation, unknown, missing)
if missing:
    raise_missing_field_error(location, annotation, missing)

try:
    return cls(**kwargs)                             # the class may refuse: `__post_init__`, `validate_dataclass`
except (SerializeError, RecursionError):
    raise
except Exception as caught:
    raise_build_failed_error(location, annotation, caught)
```

`resolve_type_hints` is the reason forward references and generics work. `get_type_hints` is
called with `include_extras=True` — its default strips `Annotated[T, rule]` to `T` and would throw
away every rule on every field — and the type variables of `Box[int]` are then replaced with the
arguments:

```python
hints = get_type_hints(cls, include_extras=True)
parameters = getattr(cls, "__parameters__", ())
mapping = dict(zip(parameters, get_args(annotation) if origin is not None else ()))
return {name: substitute_type_vars(hint, mapping) for name, hint in hints.items()}
```

**`build_named_tuple_value`** reads both shapes — an object by name (the way `serialize` writes
it) and a list by position (the way files written by hand often look). A field with a default may
be absent, from the right end of a list or anywhere in an object. A `collections.namedtuple` has
no type hints, so every field is `Any`:

```python
if isinstance(data, Mapping):                        # by name
    missing = [n for n in names if n not in data and n not in defaults]
    ...
elif isinstance(data, (list, tuple)):                # by position
    required = len([n for n in names if n not in defaults])
    if not required <= len(data) <= len(names):
        raise_wrong_length_error(location, annotation, data, required, len(names))
else:
    raise_wrong_type_error(location, annotation, data)
```

**`build_typed_dict_value`** takes the required keys from `__required_keys__`, which already
accounts for `total=False`, `Required` and `NotRequired`, and returns a plain `dict` with the keys
that were present — which is what a `TypedDict` is at run time.

**`build_alias_value` and `build_qualified_value`** are transparent. A `TypeVar` stands for its
bound (or `Any`), a `NewType` for its supertype, a `type X = ...` alias for its value; `Final[T]`,
`Required[T]`, `NotRequired[T]` and `ReadOnly[T]` say something about the *name*, not about the
value, so `T` is built. A handler registered for the name itself is found first and wins.

**`build_with_handler`** is the single place that guards the built-in handlers, which are
one-line lambdas that do not check their input. A number where a date string belongs is a
`TypeError` in there; it becomes one card with a location, the original exception as its cause:

```python
try:
    return handler(data, annotation)
except (SerializeError, RecursionError):             # already a card / handled at the top
    raise
except Exception as caught:
    raise_build_failed_error(location, annotation, caught)
```

**`DeserializeContext`** is a `slots` dataclass made anew for every call — `strict`, the
dispatcher, and the `build` method that is how every builder recurses.

[▲ Back to top](#-table-of-contents)

---

### Errors of this package

Every error is a structured card ([`simplibs-exception`](https://pypi.org/project/simplibs-exception/));
the names start with `DESERIALIZE_`. The `label` of a card is the location (`$.servers[2].port`),
the `value` is the offending data.

| Error name                           | Wraps        | Raised by                                   | When                                                              |
|--------------------------------------|--------------|---------------------------------------------|-------------------------------------------------------------------|
| `DESERIALIZE_WRONG_TYPE`             | `TypeError`  | `build_value`, primitive / container builders | The data is not the kind the annotation asks for (text for an int, a list for an object, …) |
| `DESERIALIZE_UNSUPPORTED_ANNOTATION` | `TypeError`  | `build_value`                               | The annotation is not one the library can build                   |
| `DESERIALIZE_UNION_NO_MATCH`         | `TypeError`  | `build_union_value`                         | No member of the union fits (the deepest failure is the cause)    |
| `DESERIALIZE_UNION_AMBIGUOUS`        | `TypeError`  | `build_union_value`                         | More than one member fits and none is exactly the data's type     |
| `DESERIALIZE_MISSING_FIELD`          | `ValueError` | dataclass, `NamedTuple`, `TypedDict` builders | A required field or key is absent (an excluded field without a default as well) |
| `DESERIALIZE_UNKNOWN_FIELD`          | `ValueError` | dataclass, `NamedTuple`, `TypedDict` builders | `strict=True` and the data has a key the type does not know       |
| `DESERIALIZE_WRONG_LENGTH`           | `ValueError` | `build_tuple_value`, `build_named_tuple_value` | A positional tuple or `NamedTuple` list has the wrong number of items |
| `DESERIALIZE_LITERAL_MISMATCH`       | `ValueError` | `build_literal_value`                       | The data is not one of the listed values (or has another type)    |
| `DESERIALIZE_RULE_FAILED`            | `ValueError` | `build_annotated_value`                     | A rule of `Annotated` returned `False`                            |
| `DESERIALIZE_INVALID_KEY`            | `ValueError` | `build_mapping_key`                         | No form of the key text fits the key annotation                   |
| `DESERIALIZE_KEY_COLLISION`          | `ValueError` | `build_mapping_value`                       | Two key texts become one key                                      |
| `DESERIALIZE_BUILD_FAILED`           | `ValueError` | the builders, `build_with_handler`          | A constructor, a subclass, a rule, a handler or a type-hint lookup raised (kept as cause) |
| `DESERIALIZE_DATA_TOO_DEEP`          | `ValueError` | `deserialize`                               | `RecursionError` — data nested beyond the interpreter's limit     |

A dataclass field with broken `metadata` options is the one error that is not a
`DeserializationError`: `SERIALIZE_INVALID_FIELD_OPTIONS`, a `ParamError` — see
[`serialized_field`](README_SERIALIZE_FIELDS.md).

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicdeserializer--the-way-back)
