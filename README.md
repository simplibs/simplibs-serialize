# 🔄 `simplibs-serialize`

[![PyPI](https://img.shields.io/pypi/v/simplibs-serialize)](https://pypi.org/project/simplibs-serialize/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-serialize/blob/main/LICENSE)
[![tests](https://github.com/simplibs/simplibs-serialize/actions/workflows/tests.yml/badge.svg)](https://github.com/simplibs/simplibs-serialize/actions)

**Objects out, typed objects back — and an exact card when the data does not fit.**

A Python library that turns your objects into plain, JSON-compatible data and builds **typed
objects back** from it, built around one idea: **the annotation is the schema**. Nothing is guessed
on the way out, and nothing is silently cast on the way back — a dataclass, a `list[date]` or a
`dict[Color, Point]` comes back as exactly that, or the library says precisely *where* and *why*
the data does not fit (`$.servers[2].port`), through a structured
[`simplibs-exception`](https://pypi.org/project/simplibs-exception/) card. The same two functions
are offered as JSON text, as JSON files, as composable **rules** and as pipeline **actions**.

```python
from simplibs.serialize import serialize, deserialize, to_json

to_json(task, indent=None)                  # -> '{"title": "Write docs", "due": "2026-10-25", "tags": ["docs", "serialize"]}'
deserialize(serialize(task), Task) == task  # -> True   (the date is a date again, the list a set again)
deserialize({"title": 1}, Task)             # -> raises: DESERIALIZE_WRONG_TYPE at $.title — no silent cast
```

> `simplibs-serialize` is the sister of
> [`simplibs-file`](https://pypi.org/project/simplibs-file/): that library moves **text and bytes**
> to and from the disk, this one turns **objects into the data** it writes and back. Its JSON
> functions are built directly on `write_json` and `read_json`.

---

## 🧭 The Core Philosophy

The usual way is `json.dumps(obj, default=str)`: whatever it does not know becomes a string that
looks like an answer, a `set` is written in a different order on every run, a date comes back as
text, and a typo in a config file travels on into the program. `simplibs-serialize` takes those
traps seriously:

* **Nothing is guessed on the way out.** An object nobody knows how to convert is an error — not
  `str(obj)` and not its `__dict__`. The explicit way to ask for a fallback is `default=`.
* **The annotation is the schema.** Reading is driven by the type you ask for, and every part of
  the data is **checked** against it: an `int` is an int that is not a bool, `None` is accepted only
  where the annotation allows it, and a union picks the member that is exactly the data's type.
* **Same data, same bytes.** Sets are written in a fixed order, keys are always text, dataclass
  fields keep their declaration order — the output is the same on every run and every machine.
* **Every error says where.** The location is written as `$.servers[2].host`, and the card carries
  the offending value, what was expected and how to fix it.
* **Convert first, touch the disk later.** A value that cannot be written fails with the target
  file still intact — never a half-written, invalid JSON file.
* **One definition.** `is_serializable`, `is_deserializable` and the rules built on them perform
  the **real** conversion and discard the result, so a check can never disagree with the function.
* **Extensible in one place.** `register_type` teaches the library a type of your own (or replaces
  a built-in one) for both directions, and a handler always wins over the general rule.
* **Layers that only look left.** `commons` ← `registry`, `fields` ← `serializer`, `deserializer`
  ← `json_io` ← `actions`, `rules` — every layer imports only from those before it, and the
  serializer and the deserializer never import each other.

```python
serialize(object())          # -> raises: SERIALIZE_UNSUPPORTED_TYPE at $   — never "<object at 0x...>"
deserialize("5", int)        # -> raises: DESERIALIZE_WRONG_TYPE at $       — never a silent cast
```

---

## 📦 Installation

```bash
pip install simplibs-serialize
```

Requires Python 3.11+. Runtime dependencies: [`simplibs-exception`](https://pypi.org/project/simplibs-exception/)
(the error cards), [`simplibs-validate`](https://pypi.org/project/simplibs-validate/)
(`@validate_call` and the rule checks of `Annotated`), [`simplibs-rules`](https://pypi.org/project/simplibs-rules/)
(the `Rule` classes), [`simplibs-actions`](https://pypi.org/project/simplibs-actions/) (the
`Action` classes), [`simplibs-file`](https://pypi.org/project/simplibs-file/) (`write_json` and
`read_json`), [`simplibs-path`](https://pypi.org/project/simplibs-path/) (paths) and
[`simplibs-sentinels`](https://pypi.org/project/simplibs-sentinels/) (used by the test helper). The
helper in `simplibs.serialize.testing` is meant for pytest 9 or newer, where the `subtests` fixture is built in.

---

## 🚀 Quick Start in 60 Seconds

### Level 1: Out and back

```python
from dataclasses import dataclass
from datetime import date

from simplibs.serialize import serialize, deserialize

@dataclass
class Task:
    title: str
    due: date
    tags: set[str]

task = Task("Write docs", date(2026, 10, 25), {"serialize", "docs"})

data = serialize(task)
# -> {"title": "Write docs", "due": "2026-10-25", "tags": ["docs", "serialize"]}

deserialize(data, Task)                           # -> Task(title='Write docs', due=date(2026, 10, 25), tags={...})
deserialize([1, 2, 3], list[int])                 # -> [1, 2, 3]
deserialize({"1": "a"}, dict[int, str])           # -> {1: "a"}
```

### Level 2: JSON text and files

```python
from simplibs.serialize import to_json, from_json, dump_json_file, load_json_file

text = to_json(task, indent=None)                 # -> '{"title": "Write docs", ...}'
from_json(text, Task)                             # -> Task(...)

dump_json_file("out/task.json", task, sort_keys=True)   # converted first, then written atomically
load_json_file("out/task.json", Task)                   # -> Task(...)
load_json_file("out/tasks.json", list[Task])            # -> [Task(...), ...]
```

### Level 3: Your own types

```python
from simplibs.serialize import register_type, serialized_field

@dataclass
class User:
    name: str
    user_name: str = serialized_field(alias="userName", default="")   # another name in the data
    token: str = serialized_field(exclude=True, default="")           # not data at all

serialize(User("Eva", "eva", "secret"))          # -> {"name": "Eva", "userName": "eva"}

register_type(                                    # a class the library does not know
    Point,
    to_func=lambda p: {"x": p.x, "y": p.y},
    from_func=lambda data, cls: cls(data["x"], data["y"]),
)
deserialize([{"x": 1, "y": 2}], list[Point])      # -> [Point(x=1, y=2)]
```

### Level 4: Rules and pipelines

```python
from simplibs.actions import ForEach
from simplibs.path.actions import CollectFiles
from simplibs.path.rules import HasSuffix
from simplibs.serialize.actions import DumpJsonFile, LoadJsonFile
from simplibs.serialize.rules import IsSerializable

publish = IsSerializable() >> DumpJsonFile(path="out/task.json", sort_keys=True)
publish(task)                                     # -> Path('<cwd>/out/task.json')

load_all = CollectFiles(include_filter=HasSuffix(".json")) >> ForEach(LoadJsonFile(annotation=Task))
load_all("out")                                   # -> [Task(...), ...]
```

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/serialize/
├── logic/                ◄── The functional core — plain functions, no Rule/Action knowledge
│   ├── serializer/       ◄── serialize, is_serializable
│   ├── deserializer/     ◄── deserialize, is_deserializable
│   ├── json_io/          ◄── to_json, from_json, dump_json_file, load_json_file
│   ├── registry/         ◄── register_type, unregister_type, the built-in handlers
│   └── fields/           ◄── serialized_field
├── annotations/          ◄── Named types for signatures (ToHandler, FromHandler, TargetType)
├── exceptions/           ◄── Structured exception cards (SerializeError, SerializationError, DeserializationError)
├── rules/                ◄── Rule classes (domain folder) — IsSerializable, IsDeserializable
├── actions/              ◄── Action classes over the functions (domain folder)
│   └── convert/  text/  files/  destinations/
└── testing/              ◄── Test helpers (domain folder) — assert_round_trip
```

Everything in `logic/` and the shared types and exceptions is importable straight from
`simplibs.serialize`. `rules`, `actions` and `testing` are separate domains, imported through their
own folders:

```python
from simplibs.serialize import serialize, deserialize, register_type, ToHandler, SerializeError   # functions, types, exceptions
from simplibs.serialize.rules import IsSerializable, IsDeserializable                             # rules
from simplibs.serialize.actions import Serialize, Deserialize, ToJson, FromJson                   # actions
from simplibs.serialize.testing import assert_round_trip                                          # test helper
```

---

## 📤 `logic/serializer/` — The way out

Turns **any Python object into a structure `json.dumps` accepts** — only `None`, `bool`, `int`,
`float`, `str`, `list` and `dict`. Unknown objects are an error (or go through your explicit
`default=`), sets are written in a fixed order, keys are always text, circles and `nan` are named,
and every error carries the location of the bad value.

| Function          | Description / Parameters                                                                              |
|-------------------|-------------------------------------------------------------------------------------------------------|
| `serialize`       | Converts an object to plain JSON-compatible data (`obj`, `default=None`, `allow_nan=False`).           |
| `is_serializable` | Would `serialize` succeed? A real run, not a guess (`obj`, `default=None`, `allow_nan=False`).        |

➡️ [README_SERIALIZE_SERIALIZER](https://github.com/simplibs/simplibs-serialize/blob/main/docs/logic/README_SERIALIZE_SERIALIZER.md)

---

## 📥 `logic/deserializer/` — The way back

Builds a value of the **annotation you give** from serialized data: primitives, containers, tuples,
mappings, unions, `Literal`, `Annotated` (with its rules), dataclasses (also generic), `NamedTuple`,
`TypedDict`, enums and every registered type. The data is checked, not trusted — an unknown or
missing field, a wrong type, an ambiguous union and a failed rule are each one card with a location.

| Function            | Description / Parameters                                                                            |
|---------------------|-----------------------------------------------------------------------------------------------------|
| `deserialize`       | Builds a value of the annotation from the data (`data`, `annotation`, `strict=True`).               |
| `is_deserializable` | Would `deserialize` succeed? A real run, not a guess (`data`, `annotation`, `strict=True`).         |

➡️ [README_SERIALIZE_DESERIALIZER](https://github.com/simplibs/simplibs-serialize/blob/main/docs/logic/README_SERIALIZE_DESERIALIZER.md)

---

## 📄 `logic/json_io/` — JSON text and files

The two halves on **text and on disk**. Conversion happens in memory first, so a value that cannot
be written leaves the target file untouched; the file handling (atomic swap, encoding, line
endings) is `simplibs-file`'s. Path first, like everywhere in the ecosystem.

| Function         | Description / Parameters                                                                                              |
|------------------|-----------------------------------------------------------------------------------------------------------------------|
| `to_json`        | An object as JSON text, no trailing newline (`obj`, `indent=2`, `ensure_ascii=False`, `sort_keys=False`, `allow_nan=False`, `default`). |
| `from_json`      | JSON text (or bytes) to a typed value; a syntax error carries line and column (`json_str`, `annotation`, `strict=True`). |
| `dump_json_file` | Converts, then writes atomically; returns the `Path` (`path`, `obj`, `indent`, ..., `trailing_newline=True`, `overwrite=True`, ...). |
| `load_json_file` | Reads a file and builds a typed value from it (`path`, `annotation`, `strict=True`, `encoding="utf-8-sig"`, `errors`). |

➡️ [README_SERIALIZE_JSON_IO](https://github.com/simplibs/simplibs-serialize/blob/main/docs/logic/README_SERIALIZE_JSON_IO.md)

---

## 🧩 `logic/registry/` — Teach it your types

The table of types the library converts. It knows `datetime`, `date`, `time`, `timedelta`, paths,
`UUID`, `Decimal`, `Fraction`, `bytes`, network addresses and every enum; `register_type` adds a
type of your own — or replaces a built-in handler — and `unregister_type` takes it away again (the
built-in one comes back). A handler registered for a base class serves its subclasses, and it wins
over the general rule.

| Function          | Description / Parameters                                                                              |
|-------------------|-------------------------------------------------------------------------------------------------------|
| `register_type`   | Registers a handler for a class, an annotation or a `NewType` (`type_`, `to_func=None`, `from_func=None`). |
| `unregister_type` | Removes the registration in both directions; returns `True` if anything changed (`type_`).            |

➡️ [README_SERIALIZE_REGISTRY](https://github.com/simplibs/simplibs-serialize/blob/main/docs/logic/README_SERIALIZE_REGISTRY.md)

---

## 🔖 `logic/fields/` — Fields with a name of their own

A drop-in replacement for `dataclasses.field` that says how a dataclass field appears in the data:
under another name, or not at all. The options are read by both directions from the same place.

| Function           | Description / Parameters                                                                              |
|--------------------|-------------------------------------------------------------------------------------------------------|
| `serialized_field` | `dataclasses.field` plus two options (`alias=None`, `exclude=False`, and everything `field` takes).    |

➡️ [README_SERIALIZE_FIELDS](https://github.com/simplibs/simplibs-serialize/blob/main/docs/logic/README_SERIALIZE_FIELDS.md)

---

## 📐 `rules/` — Rules for values and data

Every rule is a `Rule` from [`simplibs-rules`](https://pypi.org/project/simplibs-rules/): composable
with `&`, `|` and `~`, usable as a `@validate_call` annotation (`Annotated[dict, IsSerializable()]`)
and as a pipeline gate (`IsSerializable() >> ToJson()`). A failed rule carries the exact
`SerializationError` / `DeserializationError` — with its location — as its cause.

| Class              | Description / Parameters                                                                              |
|--------------------|-------------------------------------------------------------------------------------------------------|
| `IsSerializable`   | The value can be converted by `serialize` (`default=None`, `allow_nan=False`).                        |
| `IsDeserializable` | The data can be built into the annotation (`annotation`, `strict=True`).                              |

➡️ [README_SERIALIZE_RULES](https://github.com/simplibs/simplibs-serialize/blob/main/docs/README_SERIALIZE_RULES.md)

---

## ⚙️ `actions/` — Pipeline steps

Every function that takes one main value and returns one result is also an `Action` from
[`simplibs-actions`](https://pypi.org/project/simplibs-actions/): configured once, called with the
main input, chainable with `>>`, `&` and `|`, and awaitable through `acall`.

A file writer needs an object **and** a path, but a pipeline carries one value — so both directions
are offered: `DumpJsonFile(path=...)(obj)` (the **object** flows) and `DumpJsonFileTo(obj=...)(path)`
(the **path** flows). The annotation does not flow with the data, so `Deserialize`, `FromJson` and
`LoadJsonFile` take it as a required option.

| Group            | Actions                         | Main input → result                    |
|------------------|---------------------------------|----------------------------------------|
| **convert**      | `Serialize`, `Deserialize`      | object → structure; structure → object |
| **text**         | `ToJson`, `FromJson`            | object → `str`; `str` → object         |
| **files**        | `DumpJsonFile`, `LoadJsonFile`  | object → written `Path`; path → object |
| **destinations** | `DumpJsonFileTo`                | path → written `Path`                  |

`is_serializable`, `is_deserializable`, `register_type` and `unregister_type` have no action: a
`Rule` is already a valid pipeline step, and registration is set-up, not a step of data flow.

➡️ [README_SERIALIZE_ACTIONS](https://github.com/simplibs/simplibs-serialize/blob/main/docs/README_SERIALIZE_ACTIONS.md)

---

## 🏷️ Types for your signatures

Plain type aliases for your own handlers and wrappers — hints for the reader and the type checker,
not validators.

| Type          | Description                                                                                   |
|---------------|-----------------------------------------------------------------------------------------------|
| `ToHandler`   | `Callable[[Any], Any]` — turns an object into a value `serialize` understands.                |
| `FromHandler` | `Callable[[Any, Any], Any]` — builds an object back from `(data, annotation)`.                |
| `TargetType`  | The annotation passed to `deserialize` — a class or a typing construct (`list[int]`, `int \| None`). |

➡️ [README_SERIALIZE_ANNOTATIONS](https://github.com/simplibs/simplibs-serialize/blob/main/docs/README_SERIALIZE_ANNOTATIONS.md)

---

## 🧪 `testing/` — Test your own types

One call for the property every serializable type must have: what goes out comes back unchanged.
Every check is reported separately through the `subtests` fixture.

| Function            | Description / Parameters                                                                            |
|---------------------|-----------------------------------------------------------------------------------------------------|
| `assert_round_trip` | Checks `serialize`, its stability, `deserialize(serialize(x))` and `from_json(to_json(x))` (`subtests`, `value`, `annotation=None`, `strict=True`, `compare=None`, `check_json=True`). |

➡️ [README_SERIALIZE_TESTING](https://github.com/simplibs/simplibs-serialize/blob/main/docs/README_SERIALIZE_TESTING.md)

---

## ⚠️ Exceptions

Every error is a structured [`simplibs.exception`](https://pypi.org/project/simplibs-exception/)
card; the names start with `SERIALIZE_` or `DESERIALIZE_`. The card's `label` is the location of the
value (`$.servers[2].port`) and its `value` is the offending object. All the library's errors share
the root `SerializeError`, so one `except SerializeError` catches everything:

```
ConversionError
└── SerializeError
    ├── SerializationError      ◄── the way out
    └── DeserializationError    ◄── the way back
```

An argument of the wrong type is a `ValidationError` (via `validate_call`); the file operations of
`json_io` raise the cards of [`simplibs-file`](https://pypi.org/project/simplibs-file/)
(`NotFoundError`, `AlreadyExistsError`, `AccessError`, ...).

| Error name                                | Class                  | Wraps        | Raised when                                                          |
|-------------------------------------------|------------------------|--------------|----------------------------------------------------------------------|
| `SERIALIZE_UNSUPPORTED_TYPE`              | `SerializationError`   | `TypeError`  | No handler, no known kind and no `default` for an object             |
| `SERIALIZE_UNSUPPORTED_KEY`               | `SerializationError`   | `TypeError`  | A mapping key has no text form (a tuple)                             |
| `SERIALIZE_CIRCULAR_REFERENCE`            | `SerializationError`   | `ValueError` | An object contains itself                                            |
| `SERIALIZE_NON_FINITE_NUMBER`             | `SerializationError`   | `ValueError` | A `nan` or `inf` and `allow_nan=False`                               |
| `SERIALIZE_DUPLICATE_KEY`                 | `SerializationError`   | `ValueError` | Two keys (or aliases) become the same text                           |
| `SERIALIZE_HANDLER_FAILED`                | `SerializationError`   | `ValueError` | A handler or `default` raised an exception                           |
| `SERIALIZE_TOO_DEEP`                      | `SerializationError`   | `ValueError` | Nesting beyond the interpreter's limit                               |
| `DESERIALIZE_WRONG_TYPE`                  | `DeserializationError` | `TypeError`  | The data is not the kind the annotation asks for                     |
| `DESERIALIZE_UNSUPPORTED_ANNOTATION`      | `DeserializationError` | `TypeError`  | The annotation is not one the library can build                      |
| `DESERIALIZE_UNION_NO_MATCH`              | `DeserializationError` | `TypeError`  | No member of a union fits                                            |
| `DESERIALIZE_UNION_AMBIGUOUS`             | `DeserializationError` | `TypeError`  | More than one member fits and none is exactly the data's type        |
| `DESERIALIZE_MISSING_FIELD`               | `DeserializationError` | `ValueError` | A required field or key is absent                                    |
| `DESERIALIZE_UNKNOWN_FIELD`               | `DeserializationError` | `ValueError` | `strict=True` and the data has a key the type does not know          |
| `DESERIALIZE_WRONG_LENGTH`                | `DeserializationError` | `ValueError` | A positional tuple or `NamedTuple` list has the wrong length         |
| `DESERIALIZE_LITERAL_MISMATCH`            | `DeserializationError` | `ValueError` | The data is not one of the listed `Literal` values                   |
| `DESERIALIZE_RULE_FAILED`                 | `DeserializationError` | `ValueError` | A rule of `Annotated` returned `False`                               |
| `DESERIALIZE_INVALID_KEY`                 | `DeserializationError` | `ValueError` | No form of a key text fits the key annotation                        |
| `DESERIALIZE_KEY_COLLISION`               | `DeserializationError` | `ValueError` | Two key texts become one key                                         |
| `DESERIALIZE_BUILD_FAILED`                | `DeserializationError` | `ValueError` | A constructor, a handler or a rule raised an exception               |
| `DESERIALIZE_DATA_TOO_DEEP`               | `DeserializationError` | `ValueError` | Data nested beyond the interpreter's limit                           |
| `DESERIALIZE_INVALID_JSON`                | `DeserializationError` | `ValueError` | `from_json` meets text that is not valid JSON                        |
| `SERIALIZE_REGISTER_NO_HANDLER`           | `ParamError`           | `ValueError` | `register_type` gets neither `to_func` nor `from_func`               |
| `SERIALIZE_REGISTER_NOT_A_TYPE`           | `ParamError`           | `TypeError`  | `type_` is not a class, an annotation or a `NewType`                 |
| `SERIALIZE_REGISTER_UNHASHABLE_TYPE`      | `ParamError`           | `TypeError`  | `type_` is not hashable                                              |
| `SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS`  | `ParamError`           | `TypeError`  | `to_func` is given for something that is not a class                 |
| `SERIALIZE_INVALID_FIELD_OPTIONS`         | `ParamError`           | `ValueError` | A dataclass field's `metadata` options are broken                    |
| `IS_SERIALIZABLE_ERROR`                   | `SerializationError`   | `TypeError`  | `IsSerializable.validate` fails (the real card is the cause)         |
| `IS_DESERIALIZABLE_ERROR`                 | `DeserializationError` | `ValueError` | `IsDeserializable.validate` fails (the real card is the cause)       |
| `RULE_PARAM_INVALID`                      | `ParamError`           | `TypeError`  | A rule is built with an unusable parameter                           |

The names of the two rule errors follow the naming of rules in `simplibs-rules`, not the
`SERIALIZE_` prefix. Each helper README ends with the errors of its own package.

---

## 🔗 Related libraries

* **[`simplibs-file`](https://pypi.org/project/simplibs-file/)** — text and bytes on disk; `dump_json_file` and `load_json_file` are built on its `write_json` and `read_json`.
* **[`simplibs-path`](https://pypi.org/project/simplibs-path/)** — the paths themselves, and the scanners that feed `ForEach(LoadJsonFile(...))`.
* **[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)** — the `Rule` engine behind `simplibs.serialize.rules`.
* **[`simplibs-actions`](https://pypi.org/project/simplibs-actions/)** — the `Action` abstraction and containers behind `simplibs.serialize.actions`.
* **[`simplibs-validate`](https://pypi.org/project/simplibs-validate/)** — `@validate_call`, which validates every function argument here, and the rule checks of `Annotated`.
* **[`simplibs-exception`](https://pypi.org/project/simplibs-exception/)** — the structured exception cards.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---
