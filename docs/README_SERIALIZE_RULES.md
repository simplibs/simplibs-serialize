# 📐 `rules` — Rules for Values and Data

The `rules` package holds two `Rule` classes that ask the two questions of this library **as a
rule**: *can this value be written?* (`IsSerializable`) and *does this data fit that type?*
(`IsDeserializable`). Each is a real `Rule` from
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/), so it composes with `&`, `|` and `~`,
describes itself, and explains its failures.

```python
from simplibs.serialize.rules import IsSerializable, IsDeserializable
```

Rules are **not** exported from `simplibs.serialize` itself — they are a domain of their own,
imported through `simplibs.serialize.rules`.

Both are thin: the question is answered by [`is_serializable`](logic/README_SERIALIZE_SERIALIZER.md#is_serializable)
and [`is_deserializable`](logic/README_SERIALIZE_DESERIALIZER.md#is_deserializable), which perform the
**real** conversion and discard the result — so a rule can never disagree with `serialize` or
`deserialize`, and "serializable" has exactly one definition.

## Where rules are used

```python
# 1. As validation of your own function arguments (simplibs-validate)
Payload = Annotated[dict, IsSerializable()]

@validate_call
def publish(payload: Payload) -> None: ...

# 2. As pipeline gates (simplibs-actions) — a rule becomes a pass-through guard step
pipeline = IsSerializable() >> ToJson() >> WriteText(path="out/message.json")
checked  = IsDeserializable(Config) >> Deserialize(annotation=Config)

# 3. With a fallback branch — `|` sends a value that fails down another way
gate = IsSerializable() | IsSerializable(default=repr)

# 4. Directly
IsSerializable().is_valid({"a": [1, 2]})                       # -> True
IsDeserializable(list[int]).validate(["x"], value_name="raw")  # raises a card with a cause
```

## What every rule here guarantees

* **`is_valid` returns a strict `bool`.** `True` means the real conversion succeeded, `False` that
  it raised a `SerializationError` / `DeserializationError`.
* **`describe()` is a short noun phrase** that containers compose into readable text:
  `IsSerializable().describe()` → `"serializable value"`;
  `IsDeserializable(list[int]).describe()` → `"data for list[int]"` (the annotation is described in the same words `validate_call` prints).
* **The failure card carries the real reason.** A failed `validate` gives a card that names the
  checked value, and the **exact** `SerializationError` / `DeserializationError` — with its
  location, `$.items[2]` or `$.servers[2].port` — as its `__cause__`.
* **Constructor mistakes are `ParamError`s**, raised when the rule is built, not when it is first
  used. The options are **keyword-only** (`IsSerializable(allow_nan=True)`).
* **A broken class declaration is not hidden.** A dataclass field with invalid `metadata` options
  is a bug in the code, not a property of the value, so the `ParamError` passes through
  `is_valid` just as it does through the functions.

## A note on errors

| Situation                                                  | Exception / error name                                           |
|------------------------------------------------------------|------------------------------------------------------------------|
| A rule is built with an unusable parameter                 | `ParamError` (`RULE_PARAM_INVALID`)                              |
| A value fails `IsSerializable`                             | `SerializationError` (`IS_SERIALIZABLE_ERROR`), cause: the real card |
| Data fails `IsDeserializable`                              | `DeserializationError` (`IS_DESERIALIZABLE_ERROR`), cause: the real card |

---

## 🧭 Table of Contents

* [`IsSerializable`](#isserializable)
* [`IsDeserializable`](#isdeserializable)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-rules--rules-for-values-and-data)

---

### `IsSerializable`

The value must be convertible by `serialize` — a gate in front of `ToJson()`, `DumpJsonFile(...)`
or an API call, so a value that cannot be written is stopped **before the first side effect**.

**Parameters:**

* `default` (*ToHandler | None*, keyword-only, default `None`): The same fallback `serialize` takes. Not a function and not `None` is a `ParamError`.
* `allow_nan` (*bool*, keyword-only, default `False`): The same switch `serialize` takes. Not a `bool` is a `ParamError`.

**`describe()`:** `"serializable value"` — always, whatever the parameters.

**Example usage:**

```python
IsSerializable().is_valid({"a": [1, 2, 3]})              # -> True
IsSerializable().is_valid(date(2024, 1, 2))              # -> True    (a built-in type)
IsSerializable().is_valid(object())                      # -> False
IsSerializable().is_valid(float("nan"))                  # -> False
IsSerializable(allow_nan=True).is_valid(float("nan"))    # -> True
IsSerializable(default=repr).is_valid(object())          # -> True    (the fallback takes it)

IsSerializable().validate({"items": [1, object()]}, value_name="payload")
# -> raises: SerializationError  IS_SERIALIZABLE_ERROR   label: payload
#    cause:  SERIALIZE_UNSUPPORTED_TYPE  at  $.items[1]

IsSerializable(default=5)                                # -> raises: ParamError (RULE_PARAM_INVALID)
```

**Notes.** One definition: the rule only wraps `is_serializable`. The precise reason is **not**
in the card's own text — the card says that the value cannot be converted and points to the cause,
which has the location. A composed rule such as `IsSerializable(default=repr) & ~IsNone()` explains
its own part the same way. Error names: `IS_SERIALIZABLE_ERROR`, `RULE_PARAM_INVALID`.

<details>
<summary>🔍 Under the hood</summary>

```python
class IsSerializable(Rule):
    __slots__ = ("default", "allow_nan")

    def __init__(self, *, default: ToHandler | None = None, allow_nan: bool = False) -> None:
        if default is not None and not callable(default):
            raise_rule_param_invalid_error("IsSerializable", "default", default, "a function or None", exception=TypeError)
        if not isinstance(allow_nan, bool):
            raise_rule_param_invalid_error("IsSerializable", "allow_nan", allow_nan, "a bool", exception=TypeError)
        self.default = default
        self.allow_nan = allow_nan

    def is_valid(self, value: Any) -> bool:
        # the real conversion, discarded — the rule cannot disagree with `serialize`
        return is_serializable(value, default=self.default, allow_nan=self.allow_nan)

    def describe(self) -> str:
        return "serializable value"
```

And the failure card — the conversion is run once more to find out exactly what is wrong and where:

```python
reason: SerializationError | None = None
try:
    serialize(value, default=self.default, allow_nan=self.allow_nan)
except SerializationError as caught:
    reason = caught

exception = SerializationError(
    error_name="IS_SERIALIZABLE_ERROR",
    label=value_name or "value",
    value=value,
    problem=f"{where}The value cannot be converted by serialize(); see the cause for the exact location.",
    expected="A value serialize() can convert.",
    how_to_fix=(
        "Fix the part named by the cause (a type to register, a cycle, a NaN).",
        "Or pass `default=` to deal with unknown objects in one place.",
    ),
    exception=TypeError,
)
exception.__cause__ = reason          # the precise reason, with its location
return exception
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `IsDeserializable`

The data must be buildable into the given annotation — a gate in front of
`Deserialize(annotation=...)` or `FromJson(...)`: data that does not fit is stopped, or sent down a
fallback branch with `|`, before the real build — and `IsDeserializable(Config)` reads as what it
checks.

**Parameters:**

* `annotation` (*TargetType*): The type the data has to fit. Not checked: any annotation is acceptable to the rule, an unsupported one simply never fits.
* `strict` (*bool*, keyword-only, default `True`): The same switch `deserialize` takes. Not a `bool` is a `ParamError`.

**`describe()`:** `"data for <annotation>"` — the annotation is described in the same words the failure cards use.

**Example usage:**

```python
IsDeserializable(Point).is_valid({"x": 1, "y": 2})                  # -> True
IsDeserializable(Point).is_valid({"x": 1})                          # -> False   (y missing)
IsDeserializable(Point).is_valid({"x": 1, "y": 2, "z": 3})          # -> False   (strict: z is unknown)
IsDeserializable(Point, strict=False).is_valid({"x": 1, "y": 2, "z": 3})   # -> True

IsDeserializable(list[int]).validate(["a"], value_name="raw")
# -> raises: DeserializationError  IS_DESERIALIZABLE_ERROR   label: raw
#    cause:  DESERIALIZE_WRONG_TYPE  at  $[0]

IsDeserializable(Point, strict="no")                                # -> raises: ParamError (RULE_PARAM_INVALID)
```

**Notes.** The rule wraps `is_deserializable` and its card carries the real
`DeserializationError` as the cause — the data is built once more to find out exactly what is wrong
and where. The how-to-fix hint offers `strict=False` for the unknown-keys case. Error names:
`IS_DESERIALIZABLE_ERROR`, `RULE_PARAM_INVALID`.

<details>
<summary>🔍 Under the hood</summary>

```python
class IsDeserializable(Rule):
    __slots__ = ("annotation", "strict")

    def __init__(self, annotation: TargetType, *, strict: bool = True) -> None:
        if not isinstance(strict, bool):
            raise_rule_param_invalid_error("IsDeserializable", "strict", strict, "a bool", exception=TypeError)
        self.annotation = annotation
        self.strict = strict

    def is_valid(self, value: Any) -> bool:
        # the real build, discarded — the rule cannot disagree with `deserialize`
        return is_deserializable(value, self.annotation, strict=self.strict)

    def describe(self) -> str:
        return f"data for {describe_annotation(self.annotation)}"
```

And the failure card:

```python
reason: DeserializationError | None = None
try:
    deserialize(value, self.annotation, strict=self.strict)
except DeserializationError as caught:
    reason = caught

wanted = describe_annotation(self.annotation)
exception = DeserializationError(
    error_name="IS_DESERIALIZABLE_ERROR",
    label=value_name or "value",
    value=value,
    problem=f"{where}The data cannot be built into {wanted}; see the cause for the exact location.",
    expected=f"Data that fits {wanted}.",
    how_to_fix=(
        "Correct the part named by the cause.",
        "Or pass strict=False to ignore keys the type does not know.",
    ),
    exception=ValueError,
)
exception.__cause__ = reason          # the precise reason, with its location
return exception
```

</details>

[▲ Back to top](#-table-of-contents)

---

### Errors of this package

The names of the rules do **not** start with `SERIALIZE_` or `DESERIALIZE_`: they follow the naming
of rules in `simplibs-rules` (`<RULE>_ERROR`), and the card of a failed rule is a rule's card, with
the library's real card as its cause.

| Error name                 | Class                  | Wraps        | Raised by                        | When                                                      |
|----------------------------|------------------------|--------------|----------------------------------|-----------------------------------------------------------|
| `IS_SERIALIZABLE_ERROR`    | `SerializationError`   | `TypeError`  | `IsSerializable.build_exception` | `validate` of a value `serialize` cannot convert          |
| `IS_DESERIALIZABLE_ERROR`  | `DeserializationError` | `ValueError` | `IsDeserializable.build_exception` | `validate` of data that does not fit the annotation     |
| `RULE_PARAM_INVALID`       | `ParamError`           | `TypeError`  | both constructors                | `default` is not a function or `None`; `allow_nan` or `strict` is not a `bool` |

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-rules--rules-for-values-and-data)
