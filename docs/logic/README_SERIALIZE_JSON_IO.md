# 📄 `logic/json_io` — JSON Text and Files

The `json_io` package puts the two halves of the library **on text and on disk**: four functions
that go from an object to JSON text or a JSON file, and back from text or a file to an object of a
given type. They add no rules of their own — the conversion is [`serialize`](README_SERIALIZE_SERIALIZER.md)
and [`deserialize`](README_SERIALIZE_DESERIALIZER.md), the file handling is
[`simplibs-file`](https://pypi.org/project/simplibs-file/) — this package is the glue, and it is
written so that nothing is repeated.

```python
from simplibs.serialize import to_json, from_json, dump_json_file, load_json_file

text = to_json(config)                         # -> '{\n  "port": 8080, ...}'
config = from_json(text, Config)               # -> Config(port=8080, ...)

dump_json_file("out/config.json", config)      # -> Path("out/config.json")
config = load_json_file("out/config.json", Config)
```

All four are wrapped in `@validate_call`, so a wrong type of a parameter is rejected with a
`ValidationError` before the body runs. Each has an [action counterpart](../README_SERIALIZE_ACTIONS.md)
for pipelines (`ToJson`, `FromJson`, `DumpJsonFile`, `LoadJsonFile`).

## A note on "convert first, touch the disk second"

`to_json` and `dump_json_file` **convert in memory before anything else happens**. A value that
cannot be written — an unknown type, a circle, a `nan` — fails with a `SerializationError` that
names the exact place (`$.items[2].name`), and the target file is **completely untouched**. The
standard `json.dump` writes in chunks, so a `TypeError` in the middle of a large structure leaves
a half-written, invalid file behind.

The conversion also is the reason `sort_keys` is safe here: `json.dumps(sort_keys=True)` fails on a
dict with keys of mixed types, but after `serialize` every key is text, so it cannot fail.

## A note on "path first"

`dump_json_file(path, obj)` and `load_json_file(path, annotation)` take the path **first**, like
`write_json(path, data)`, `read_json(path)` and `write_text(path, text)` in `simplibs-file`. One order
across the ecosystem is easier to remember than agreement with the standard library's function that
takes a file handle (`json.dump(obj, fp)`).

## A note on "two steps on purpose"

`dump_json_file` could hand the original object and a `default` to `write_json` and let
`json.dumps` convert it. It does not: then the library's own rules — dataclasses, enums, registered
types, locations in errors — would never run. So the object is converted by `serialize` first and
`write_json` only writes the **structure**; everything about the file (the draft and the atomic
swap, the encoding, the line ending, `overwrite`) is its business, and a fix there holds here.

## A note on reading

* **A BOM is not part of the JSON.** `from_json` drops a byte-order mark at the start of a `str`
  (bytes are handled by `json.loads` itself); `load_json_file` reads with `utf-8-sig` by default,
  so a file saved with a BOM by an editor just works.
* **`NaN` and `Infinity` are read.** `json.loads` accepts them and so does this package — the same
  leniency as `read_json`. A `float` field takes them; an `Annotated` rule decides whether that is
  acceptable.
* **Two kinds of failure.** A text that is not JSON fails first (`DESERIALIZE_INVALID_JSON`, with
  line and column); JSON that does not fit the type fails in `deserialize`, with the location of the
  bad value. For a *file*, a content that is not valid text or JSON is reported by `read_json`
  (a `ConversionError` from `simplibs-file`) before `deserialize` is reached. All of them are a
  `ConversionError`, so one `except ConversionError` covers a bad file as a whole.

## A note on errors

| Situation                                                       | Exception              |
|-----------------------------------------------------------------|------------------------|
| An object cannot be converted (as for `serialize`)              | `SerializationError`   |
| The text is not valid JSON (with line and column)               | `DeserializationError` (`DESERIALIZE_INVALID_JSON`) |
| The JSON does not fit the annotation (as for `deserialize`)     | `DeserializationError` |
| The file is missing / a directory occupies the path             | `NotFoundError` / `StateError` (from `simplibs-file`) |
| The target exists and `overwrite=False`                         | `AlreadyExistsError`   |
| The OS refuses (permissions, a locked file, a full disk)        | `AccessError`          |
| A file is not valid text or JSON                                | `ConversionError` (from `read_json`) |

---

## 🧭 Table of Contents

* [`to_json`](#to_json)
* [`from_json`](#from_json)
* [`dump_json_file`](#dump_json_file)
* [`load_json_file`](#load_json_file)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../../README.md#-logicjson_io--json-text-and-files)

---

### `to_json`

Converts an object to JSON text — for a message, a log line, a response body, anything that is
text and not a file.

**Parameters:**

* `obj` (*Any*): The object to write.
* `indent` (*int | str | None*, keyword-only, default `2`): Indentation: a number of spaces, a string such as `"\t"`, or `None` for compact one-line output.
* `ensure_ascii` (*bool*, keyword-only, default `False`): If `False`, non-ASCII text is written as it is (`č`, not `\u010d`).
* `sort_keys` (*bool*, keyword-only, default `False`): If `True`, object keys are sorted — reproducible output.
* `allow_nan` (*bool*, keyword-only, default `False`): If `False`, `NaN` and `Infinity` are an error, because they are not valid JSON.
* `default` (*ToHandler | None*, keyword-only, default `None`): The fallback for an object nothing else can convert; see [`serialize`](README_SERIALIZE_SERIALIZER.md#serialize).

**Returns:**

* `str`: The JSON text, **without** a trailing newline.

**Raises:**

* `SerializationError`: As for `serialize` — see its [errors](README_SERIALIZE_SERIALIZER.md#errors-of-this-package).
* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options.

**Example usage:**

```python
to_json({"name": "Čech", "n": [1, 2]}, indent=None)     # -> '{"name": "Čech", "n": [1, 2]}'
to_json({"name": "Čech"}, indent=None, ensure_ascii=True)  # -> '{"name": "\\u010dech"}'
to_json({"b": 1, "a": 2}, indent=None, sort_keys=True)  # -> '{"a": 2, "b": 1}'
to_json({1, 2, 3})                                      # -> '[\n  1,\n  2,\n  3\n]'
to_json(float("nan"))                                   # -> raises: SERIALIZE_NON_FINITE_NUMBER
to_json(object(), default=repr, indent=None)            # -> '"<object object at 0x...>"'
```

**No trailing newline.** A string is a value; a newline belongs to a *file*, and
`dump_json_file` adds it (`trailing_newline=True`).

**Under the hood:**
```python
# 1. Convert to a structure first — anything wrong is found here, with its location
structure = serialize(obj, default=default, allow_nan=allow_nan)

# 2. Write it as text; a structure `serialize` made cannot fail here
return json.dumps(
    structure,
    indent=indent,
    ensure_ascii=ensure_ascii,
    sort_keys=sort_keys,
    allow_nan=allow_nan,
)
```

> 💡 `ensure_ascii=False` is the default on purpose: a file or a message written for people should
> stay readable. Turn it on only for a reader that cannot take anything but ASCII.

[▲ Back to top](#-table-of-contents)

---

### `from_json`

Reads JSON text and builds a value of the given type from it — the text-in counterpart of
[`deserialize`](README_SERIALIZE_DESERIALIZER.md#deserialize).

**Parameters:**

* `json_str` (*str | bytes*): The JSON text (or UTF-8 bytes).
* `annotation` (*TargetType*): What to build: a class, `list[Point]`, `dict[str, int]`, …
* `strict` (*bool*, keyword-only, default `True`): As for `deserialize`: unknown keys are an error.

**Returns:**

* *Any*: A value of the requested type.

**Raises:**

* `DeserializationError` (`DESERIALIZE_INVALID_JSON`): The text is not valid JSON (the card has the line and column), is nested too deep to read, or cannot be read as JSON.
* `DeserializationError`: The JSON does not fit the annotation — as for `deserialize`.
* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options.

**Example usage:**

```python
from_json('{"x": 1, "y": 2}', Point)           # -> Point(x=1, y=2)
from_json("[1, 2, 3]", list[int])              # -> [1, 2, 3]
from_json(b'{"x": 1, "y": 2}', Point)          # -> Point(x=1, y=2)    (bytes are fine)
from_json("\ufeff[1]", list[int])              # -> [1]                (a BOM is dropped)

from_json('{"x": 1,}', Point)                  # -> raises: DESERIALIZE_INVALID_JSON  at line 1, column 9
from_json('{"x": "a", "y": 2}', Point)         # -> raises: DESERIALIZE_WRONG_TYPE    at $.x
```

**Under the hood:**
```python
# 1. A BOM in front of text is not part of the JSON (bytes are handled by `json.loads`)
if isinstance(json_str, str):
    json_str = json_str.removeprefix("\ufeff")

# 2. Parse; a syntax error becomes a card with a position and an excerpt
try:
    data = json.loads(json_str)
except (ValueError, RecursionError) as caught:
    raise_invalid_json_error(json_str, caught)

# 3. Build the value
return deserialize(data, annotation, strict=strict)
```

> 💡 A text nested beyond the interpreter's limit raises `RecursionError` inside `json.loads`; it
> becomes the same invalid-JSON card instead of crashing the caller.

[▲ Back to top](#-table-of-contents)

---

### `dump_json_file`

Writes an object to a JSON file — converted in memory first, then written atomically by
`simplibs.file.write_json`.

**Parameters:**

* `path` (*PathLike*): The target file. Its folder is created if missing.
* `obj` (*Any*): The object to write.
* `indent` (*int | str | None*, keyword-only, default `2`): Indentation: a number of spaces, a string, or `None` for compact output.
* `ensure_ascii` (*bool*, keyword-only, default `False`): If `False`, non-ASCII text is written as it is.
* `sort_keys` (*bool*, keyword-only, default `False`): If `True`, object keys are sorted — clean diffs.
* `allow_nan` (*bool*, keyword-only, default `False`): If `False`, `NaN` and `Infinity` are an error.
* `default` (*ToHandler | None*, keyword-only, default `None`): The fallback for an object nothing else can convert; see `serialize`.
* `trailing_newline` (*bool*, keyword-only, default `True`): If `True`, the file ends with a line ending.
* `encoding` (*EncodingName*, keyword-only, default `"utf-8"`): The text encoding of the file.
* `newline` (*NewlineMode*, keyword-only, default `"\n"`): The line ending written for every `"\n"`.
* `overwrite` (*bool*, keyword-only, default `True`): If `False`, an existing file is an error instead of being replaced.
* `use_draft` (*bool*, keyword-only, default `True`): Draft-and-swap write, or an in-place write.
* `sync` (*bool*, keyword-only, default `False`): Force the data to stable storage before the swap.

**Returns:**

* `Path`: The normalized target.

**Raises:**

* `SerializationError`: The object cannot be converted — the file is not touched.
* `AlreadyExistsError`: The target exists and `overwrite=False`.
* `StateError`: A directory occupies the target.
* `AccessError`: The OS refuses the write.
* `ConversionError`: A character cannot be encoded in `encoding`.

**Example usage:**

```python
dump_json_file("out/config.json", config)                    # -> Path("out/config.json")
dump_json_file("out/config.json", config, sort_keys=True)    # keys in alphabetical order — clean diffs
dump_json_file("out/config.json", config, overwrite=False)   # -> raises: AlreadyExistsError, if it exists
dump_json_file("out/bad.json", {"x": object()})              # -> raises: SERIALIZE_UNSUPPORTED_TYPE at $.x
                                                             #    (and out/bad.json was not created)
```

The path, the encoding, the draft and the line ending are explained in the
[`write` package of `simplibs-file`](https://pypi.org/project/simplibs-file/) — this function passes
them on unchanged.

**Under the hood:**
```python
# 1. Convert first — an unsupported value never reaches the file system
structure = serialize(obj, default=default, allow_nan=allow_nan)

# 2. Everything about the file is `write_json`'s business
return write_json(
    path,
    structure,
    indent=indent,
    ensure_ascii=ensure_ascii,
    sort_keys=sort_keys,
    allow_nan=allow_nan,
    trailing_newline=trailing_newline,
    encoding=encoding,
    newline=newline,
    overwrite=overwrite,
    use_draft=use_draft,
    sync=sync,
)
```

> 💡 Unlike `to_json`, the file ends with a newline by default — a text file that does not is a
> diff full of "no newline at end of file".

[▲ Back to top](#-table-of-contents)

---

### `load_json_file`

Reads a JSON file and builds a value of the given type from it.

**Parameters:**

* `path` (*PathLike*): The JSON file.
* `annotation` (*TargetType*): What to build: a class, `list[Point]`, `dict[str, int]`, …
* `strict` (*bool*, keyword-only, default `True`): As for `deserialize`: unknown keys are an error.
* `encoding` (*EncodingName*, keyword-only, default `"utf-8-sig"`): The text encoding. The default tolerates a BOM.
* `errors` (*EncodingErrors*, keyword-only, default `"strict"`): How to treat bytes the encoding cannot decode.

**Returns:**

* *Any*: A value of the requested type.

**Raises:**

* `DeserializationError`: The JSON does not fit the annotation — the card names the location of the bad value.
* `ConversionError`: The file is not valid text or valid JSON (from `read_json`).
* `NotFoundError`, `StateError`, `AccessError`: As for `read_json` — a missing file, a directory, a refused read.
* `ParamError` (`SERIALIZE_INVALID_FIELD_OPTIONS`): A dataclass field carries broken `metadata` options.

**Example usage:**

```python
load_json_file("config.json", Config)                 # -> Config(port=8080, ...)
load_json_file("points.json", list[Point])            # -> [Point(x=1, y=2), ...]
load_json_file("config.json", Config, strict=False)   # unknown keys in the file are ignored
load_json_file("missing.json", Config)                # -> raises: NotFoundError
load_json_file("broken.json", Config)                 # -> raises: ConversionError (not JSON)
load_json_file("wrong.json", Config)                  # -> raises: DESERIALIZE_WRONG_TYPE at $.port
```

**Under the hood:**
```python
# 1. Reading and parsing — BOM, encoding, syntax errors with a position — is `read_json`
data = read_json(path, encoding=encoding, errors=errors)

# 2. Build the value
return deserialize(data, annotation, strict=strict)
```

> 💡 There is no `trailing_newline` or `newline` here: reading does not care. The line endings of
> the file are whatever `read_json` makes of them.

[▲ Back to top](#-table-of-contents)

---

### Errors of this package

The package adds exactly one error of its own; everything else is passed through from
[`serialize`](README_SERIALIZE_SERIALIZER.md#errors-of-this-package),
[`deserialize`](README_SERIALIZE_DESERIALIZER.md#errors-of-this-package) or `simplibs-file`.

| Error name                 | Class                  | Wraps        | Raised by   | When                                                               |
|----------------------------|------------------------|--------------|-------------|--------------------------------------------------------------------|
| `DESERIALIZE_INVALID_JSON` | `DeserializationError` | `ValueError` | `from_json` | The text is not valid JSON (line and column named), nested too deep, or unreadable as JSON |

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicjson_io--json-text-and-files)
