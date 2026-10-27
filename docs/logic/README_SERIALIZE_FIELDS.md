# 🔖 `logic/fields` — Fields With a Name of Their Own

The `fields` package holds the one function that lets a dataclass field **say how it appears in
the data**: under another name (`userName` for `user_name`), or not at all (a cache, an open
handle, a secret). It is the drop-in replacement for `dataclasses.field` — it takes everything
`field` takes, plus two options.

```python
from simplibs.serialize import serialized_field

@dataclass
class User:
    user_name: str = serialized_field(alias="userName", default="")
    cache: dict = serialized_field(exclude=True, default_factory=dict)
```

The options are read by [`serialize`](README_SERIALIZE_SERIALIZER.md) and
[`deserialize`](README_SERIALIZE_DESERIALIZER.md) — both from the **same** place, so they can never
disagree about what a field is called in the data. The function is wrapped in `@validate_call`, so a
wrong type of `alias` or `exclude` is rejected with a `ValidationError` at the class definition.

## A note on "where it is said"

Foreign formats do not follow Python naming, and some attributes belong to the object but not to
the file. Both are stated **where the field is declared**, in the standard place for it —
`field(metadata=...)` — and not in a second configuration object, which would live far from the
class and drift from it. And not as `Annotated[str, Alias("userName")]` either: that would need
`serialize` to read the type hints of every class on every call, while the field metadata is read
directly and costs nothing for a field that has none.

## A note on what is written down

Only the options that were **asked for** are stored, under one namespaced key of the field's
`metadata` — `"simplibs.serialize"` — so they cannot collide with anybody else's metadata, and
your own `metadata` survives untouched. A field with no options is equal to a plain
`dataclasses.field`.

```python
serialized_field(alias="userName").metadata
# -> mappingproxy({"simplibs.serialize": {"alias": "userName"}})
```

## A note on being strict

The options are read by one function (`get_field_options`), and it refuses anything it does not
understand. `serialized_field` itself cannot produce a wrong option, but a hand-written
`metadata={"simplibs.serialize": {"alais": "x"}}` can — and a silently ignored alias is a bug that
shows up as data in the wrong place. The mistake is in the **class declaration**, not in the data
being converted, so it is a `ParamError`, and it is raised by `serialize`, `deserialize` and also
by `is_serializable` / `is_deserializable` — those answer "is this data fine", not "is my class
declared correctly".

## A note on alias and exclusion

* **Alias.** The field is written under the alias and read back from it. The location in an error
  uses the name **in the data** (`$.userName`), because that is what the reader of the file sees.
  Two fields that end up under one name are an error (`SERIALIZE_DUPLICATE_KEY`).
* **Exclusion.** The field is left out of the data. Give such a field a **default**, otherwise
  `deserialize` can never build the object back and reports it as missing.
* **`init=False`** is a different thing, and the two do not mix up: an `init=False` field *is*
  written (it is part of the object's state), may be present when reading, and is never passed to
  the constructor.

## A note on errors

| Situation                                                       | Exception    |
|-----------------------------------------------------------------|--------------|
| A wrong type of an argument (`alias=5`, `exclude="yes"`)        | `ValidationError` — at the class definition |
| A field's `metadata` options are broken (hand-written metadata) | `ParamError` — at the first `serialize` / `deserialize` of the class |

---

## 🧭 Table of Contents

* [`serialized_field`](#serialized_field)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../../README.md#-logicfields--fields-with-a-name-of-their-own)

---

### `serialized_field`

Declares a dataclass field with a name of its own in the data, or one that is no data at all —
the function you reach for in a dataclass body instead of `dataclasses.field`.

**Parameters:**

* `alias` (*str | None*, keyword-only, default `None`): The name the field has in the data (`userName` for `user_name`).
* `exclude` (*bool*, keyword-only, default `False`): If `True`, `serialize` leaves the field out. Give such a field a default.
* `default` (*Any*, keyword-only): As in `dataclasses.field`.
* `default_factory` (*Any*, keyword-only): As in `dataclasses.field`.
* `init` (*bool*, keyword-only, default `True`): As in `dataclasses.field`.
* `repr` (*bool*, keyword-only, default `True`): As in `dataclasses.field`.
* `hash` (*bool | None*, keyword-only, default `None`): As in `dataclasses.field`.
* `compare` (*bool*, keyword-only, default `True`): As in `dataclasses.field`.
* `metadata` (*Mapping[str, Any] | None*, keyword-only, default `None`): As in `dataclasses.field`; the serialize options are added to it.
* `kw_only` (*Any*, keyword-only): As in `dataclasses.field`.

**Returns:**

* *Any*: The field, to be assigned in a dataclass body.

**Raises:**

* `ValidationError`: A parameter has a wrong type.

**Example usage:**

```python
@dataclass
class User:
    name: str
    user_name: str = serialized_field(alias="userName", default="")
    token: str = serialized_field(exclude=True, default="")

serialize(User("Eva", "eva", "secret"))
# -> {"name": "Eva", "userName": "eva"}               (the alias is used, the token is left out)

deserialize({"name": "Eva", "userName": "eva"}, User)
# -> User(name="Eva", user_name="eva", token="")      (the excluded field comes from its default)

deserialize({"name": "Eva", "user_name": "eva"}, User)
# -> raises: DESERIALIZE_UNKNOWN_FIELD (user_name) — the data uses the alias
```

**A drop-in for `dataclasses.field`.** Every parameter is the same, so
`serialized_field(default=0)` works anywhere `field(default=0)` does. The two shadowed names
(`repr`, `hash`) are `dataclasses.field`'s own.

**Under the hood:**
```python
# 1. Only the options that were asked for are written down
options: dict[str, Any] = {}
if alias is not None:
    options[FIELD_ALIAS_OPTION] = alias
if exclude:
    options[FIELD_EXCLUDE_OPTION] = True

# 2. They join the caller's own metadata under one namespaced key
merged: dict[Any, Any] = dict(metadata) if metadata else {}
if options:
    merged[FIELD_METADATA_KEY] = options                 # "simplibs.serialize"

# 3. The rest is exactly `dataclasses.field`
return dataclasses.field(
    default=default, default_factory=default_factory, init=init, repr=repr,
    hash=hash, compare=compare, metadata=merged, kw_only=kw_only,
)
```

And the single reader, used by both directions — it is strict about every part of the options:

```python
options = field.metadata.get(FIELD_METADATA_KEY)
if options is None:                                      # a field without options is the common case
    return field.name, False

if not isinstance(options, Mapping):
    raise_invalid_field_options_error(field.name, options, "The options are not a mapping.")

unknown = set(options) - {FIELD_ALIAS_OPTION, FIELD_EXCLUDE_OPTION}
if unknown:                                              # a typo such as "alais" would be ignored without a trace
    raise_invalid_field_options_error(
        field.name, options, f"Unknown option(s): {', '.join(sorted(map(repr, unknown)))}.",
    )

alias = options.get(FIELD_ALIAS_OPTION)
if alias is not None and (not isinstance(alias, str) or not alias):
    raise_invalid_field_options_error(field.name, options, "The alias is not a non-empty text.")

exclude = options.get(FIELD_EXCLUDE_OPTION, False)
if not isinstance(exclude, bool):
    raise_invalid_field_options_error(field.name, options, "The exclusion is not a bool.")

return (alias if alias is not None else field.name), exclude
```

> 💡 `alias=""` is a `str`, so `serialized_field` itself accepts it — it is refused later, when the
> options are first read (`serialize` or `deserialize` of the class), as "the alias is not a
> non-empty text".

[▲ Back to top](#-table-of-contents)

---

### Errors of this package

| Error name                        | Class        | Wraps        | Raised by           | When                                                    |
|-----------------------------------|--------------|--------------|---------------------|---------------------------------------------------------|
| `SERIALIZE_INVALID_FIELD_OPTIONS` | `ParamError` | `ValueError` | `get_field_options` | The options are not a mapping; contain an unknown option; the alias is not a non-empty text; the exclusion is not a bool |

The card's `label` is `field '<name>' metadata` and its `value` is what was found under the
`"simplibs.serialize"` key.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicfields--fields-with-a-name-of-their-own)
