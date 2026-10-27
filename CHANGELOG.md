# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-10-27

### ✨ Added

#### Serializer — the way out

* `serialize(obj, *, default=None, allow_nan=False)` — converts any supported object to a structure `json.dumps` accepts: only `None`, `bool`, `int`, `float`, `str`, `list` and `dict`
* `is_serializable(obj, *, default=None, allow_nan=False)` — whether `serialize` would succeed; a real run whose result is discarded, so it cannot disagree with `serialize`; only a `SerializationError` means `False`
* An object nobody knows how to convert is an error — never `str(obj)` and never its `__dict__`; `default=` is the explicit fallback, called only for what nothing else knows, and its result is converted again
* One ordered list of decisions: a registered or built-in handler, a subclass of `str`/`int`/`float`, a `NamedTuple`, any mapping, a dataclass instance, any sequence or set, then `default`
* Sets are written in a fixed order (natural order, else by their JSON text), mapping keys are always text (`1` → `"1"`, `True` → `"true"`, `None` → `"null"`, an enum by its value), dataclass fields keep their declaration order
* A circle is an error while the same object used side by side is fine; `nan` and `inf` are an error unless `allow_nan=True`; endless nesting is a card, not a bare `RecursionError`
* Every error names the location of the bad value (`$.servers[2].host`, a key with a dot or a space is quoted: `$['user-name']`)

#### Deserializer — the way back

* `deserialize(data, annotation, *, strict=True)` — builds a value of the given annotation from serialized data; the annotation is the schema, and every part of the data is checked against it
* `is_deserializable(data, annotation, *, strict=True)` — whether `deserialize` would succeed; a real run whose result is discarded; only a `DeserializationError` means `False`
* Builds primitives and their subclasses, `list`, `set`, `frozenset`, `deque` and the abstract collections, `tuple` (bare, `tuple[T, ...]`, `tuple[A, B]`, `tuple[()]`), mappings with keys read back from text, unions and `Optional`, `Literal`, `Annotated`, dataclasses (also generic), `NamedTuple`, `TypedDict`, enums, `NewType`, `type` aliases, `TypeVar`, `Final`, `Required`, `NotRequired`, `ReadOnly` and every registered type
* Primitives are checked, not cast: an `int` is an int that is not a bool, a `float` takes an `int` but never a bool, and `None` is accepted only where the annotation allows it
* A union picks the member that is exactly the data's own JSON type; no match and a real tie are cards of their own, and the failure that got deepest into the data is attached as the cause
* `strict=True` refuses keys a dataclass, `NamedTuple` or `TypedDict` does not know, reported together with the missing ones; `strict=False` ignores them
* Dataclass fields are built against their own types — forward references, string annotations and generics are resolved, `Annotated` rules are kept, an alias is read from the data, an excluded field comes from its default, an `init=False` field is accepted in the data but never passed to the constructor
* The rules in `Annotated` metadata (a `Rule` or a plain predicate) are checked; a failed one is a `DeserializationError` with the location
* Mapping keys are read back by the annotation (`"1"` is a `str`, an `int`, or an `IntEnum` member as asked); two texts that become one key are an error

#### JSON text and files

* `to_json(obj, *, indent=2, ensure_ascii=False, sort_keys=False, allow_nan=False, default=None)` — the object as JSON text, without a trailing newline
* `from_json(json_str, annotation, *, strict=True)` — JSON text (or UTF-8 bytes) to a typed value; a BOM is dropped, a syntax error carries the line and column
* `dump_json_file(path, obj, *, indent, ensure_ascii, sort_keys, allow_nan, default, trailing_newline=True, encoding, newline, overwrite=True, use_draft=True, sync=False)` — converts in memory first, then writes atomically through `simplibs-file`; a value that cannot be written leaves the target file untouched; returns the `Path`
* `load_json_file(path, annotation, *, strict=True, encoding="utf-8-sig", errors="strict")` — reads a file through `simplibs-file` and builds a typed value from it
* The path comes first, like everywhere in the ecosystem

#### Registry — your own types

* `register_type(type_, *, to_func=None, from_func=None)` — registers a handler for a class, a subscripted annotation or a `NewType`; replaces a built-in handler; `to_func` needs a class
* `unregister_type(type_)` — removes the registration in both directions and restores a replaced built-in handler; returns whether anything changed, and is safe to call twice
* Built in: `datetime`, `date`, `time` (ISO text), `timedelta` (seconds), `PurePath` and its family (text with `/`), `UUID`, `Decimal`, `Fraction` (text), `bytes` and `bytearray` (strict base64), `IPv4`/`IPv6` addresses and networks, and every `Enum` (by its value)
* A handler is found by an exact match first, then along the class hierarchy, so a handler for a base class serves its subclasses; a handler always wins over the general rule
* Every built-in reader checks the kind of its input before the class is called; a handler that raises becomes one card with the location and the original exception as its cause

#### Fields

* `serialized_field(*, alias=None, exclude=False, ...)` — a drop-in replacement for `dataclasses.field` (it takes everything `field` takes) that gives a dataclass field another name in the data or leaves it out; the options live under one namespaced key of the field's `metadata` and are read by both directions from the same place

#### Rules — `simplibs.serialize.rules`

* `IsSerializable(*, default=None, allow_nan=False)` — the value can be converted by `serialize`
* `IsDeserializable(annotation, *, strict=True)` — the data can be built into the annotation
* Every rule returns a strict `bool`, describes itself (`describe()`), composes with `&`, `|` and `~`, works as a `@validate_call` annotation and as a pipeline gate; a failed `validate` carries the exact `SerializationError` / `DeserializationError`, with its location, as its cause

#### Actions — `simplibs.serialize.actions`

* Convert: `Serialize`, `Deserialize`
* Text: `ToJson`, `FromJson`
* Files, the object flows: `DumpJsonFile`; the path flows: `LoadJsonFile`
* Destinations, the path flows: `DumpJsonFileTo`
* Chainable with `>>`, `&` and `|`, awaitable through `acall`, and usable directly behind a `Rule` (`IsSerializable() >> ToJson()`)

#### Annotations

* `ToHandler` — `Callable[[Any], Any]`, the shape of a `to_func` and of `default`
* `FromHandler` — `Callable[[Any, Any], Any]`, the shape of a `from_func`, called as `from_func(data, annotation)`
* `JsonValue` — everything `serialize` can return
* `TargetType` — the annotation passed to `deserialize`
* Plain type aliases for the reader and the type checker, not validators

#### Testing — `simplibs.serialize.testing`

* `assert_round_trip(subtests, value, annotation=None, *, strict=True, compare=None, check_json=True)` — four checks reported separately through the `subtests` fixture: the data is valid JSON-compatible data, it is the same on every call, `deserialize(serialize(value))` equals the value and `from_json(to_json(value))` equals the value

#### Exceptions

* `SerializeError` (a `ConversionError`), the root of the library's errors, with `SerializationError` and `DeserializationError` below it; all are exported from `simplibs.serialize`
* Error names: `DESERIALIZE_BUILD_FAILED`, `DESERIALIZE_DATA_TOO_DEEP`, `DESERIALIZE_INVALID_JSON`, `DESERIALIZE_INVALID_KEY`, `DESERIALIZE_KEY_COLLISION`, `DESERIALIZE_LITERAL_MISMATCH`, `DESERIALIZE_MISSING_FIELD`, `DESERIALIZE_RULE_FAILED`, `DESERIALIZE_UNION_AMBIGUOUS`, `DESERIALIZE_UNION_NO_MATCH`, `DESERIALIZE_UNKNOWN_FIELD`, `DESERIALIZE_UNSUPPORTED_ANNOTATION`, `DESERIALIZE_WRONG_LENGTH`, `DESERIALIZE_WRONG_TYPE`, `IS_DESERIALIZABLE_ERROR`, `IS_SERIALIZABLE_ERROR`, `RULE_PARAM_INVALID`, `SERIALIZE_CIRCULAR_REFERENCE`, `SERIALIZE_DUPLICATE_KEY`, `SERIALIZE_HANDLER_FAILED`, `SERIALIZE_INVALID_FIELD_OPTIONS`, `SERIALIZE_NON_FINITE_NUMBER`, `SERIALIZE_REGISTER_NO_HANDLER`, `SERIALIZE_REGISTER_NOT_A_TYPE`, `SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS`, `SERIALIZE_REGISTER_UNHASHABLE_TYPE`, `SERIALIZE_TOO_DEEP`, `SERIALIZE_UNSUPPORTED_KEY`, `SERIALIZE_UNSUPPORTED_TYPE`            <!-- EVERY name from the code, no more, no less -->

#### Package Layout

* `simplibs.serialize` exports the functions, the three exceptions and the four annotations directly; `rules`, `actions` and `testing` are domain packages with their own `__all__`
* `PathLike`, `EncodingName`, `EncodingErrors` and `NewlineMode` are reused from `simplibs.path` and `simplibs.file`

#### Typing

* `py.typed` marker — the package ships its type information (declared in `package-data`, so it is part of the built wheel)

#### Documentation

* Main `README.md` with a quick start in four levels, the package structure, the domain sections and the table of all error names
* Detailed references in `docs/`: `README_SERIALIZE_SERIALIZER`, `README_SERIALIZE_DESERIALIZER`, `README_SERIALIZE_JSON_IO`, `README_SERIALIZE_REGISTRY` and `README_SERIALIZE_FIELDS` under `docs/logic/`, `README_SERIALIZE_RULES`, `README_SERIALIZE_ACTIONS` and `README_SERIALIZE_ANNOTATIONS`, and `README_SERIALIZE_TESTING` under `docs/testing/` — one card per function, class or action, with a view under the hood

#### Tests & CI

* GitHub Actions workflow (`.github/workflows/tests.yml`) running the test suite with coverage on Linux, Windows and macOS with Python 3.11, 3.12 and 3.13, and a `tests` badge in the README
* `dev` extra: `pytest>=9.0` and `pytest-cov>=5.0`

#### Dependencies

* `simplibs-exception` — the structured cards behind every error, and `ConversionError`, the base of `SerializeError`
* `simplibs-validate` — `@validate_call` on the public functions and the rule checks of `Annotated` in `deserialize`
* `simplibs-rules` — the `Rule` engine behind `simplibs.serialize.rules`
* `simplibs-actions` — the `Action` abstraction behind `simplibs.serialize.actions`
* `simplibs-file` — `write_json` and `read_json` behind the JSON file functions, and the `EncodingName`, `EncodingErrors` and `NewlineMode` annotations
* `simplibs-path` — `PathLike` for the file functions
* `simplibs-sentinels` — `UNSET` in `simplibs.serialize.testing`

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)
