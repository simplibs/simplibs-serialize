from .closest_failure import closest_failure
from .has_default import has_default
from .is_alias_annotation import is_alias_annotation
from .is_exact_type_match import is_exact_type_match
from .is_rule_like import is_rule_like
from .key_candidates import key_candidates
from .name_json_type import name_json_type
from .resolve_type_hints import resolve_type_hints


_DESIGN_NOTES = """
# Deserializer Helpers Sub-Package

## Purpose
Small private helpers of the way back: the pieces that are not a decision of their
own. What both directions need is in `logic/_helpers`.

## Internal Components Registry

| Component             | Type     | Description                                                              |
| :-------------------- | :------- | :----------------------------------------------------------------------- |
| `closest_failure`     | Function | Of several failed union members, the one that got deepest into the data. |
| `has_default`         | Function | May this dataclass field be left out of the constructor call.            |
| `is_alias_annotation` | Function | `NewType`, `type` alias or `TypeVar`.                                    |
| `is_exact_type_match` | Function | The tie-breaker of a union: the data is exactly the member's primitive.  |
| `is_rule_like`        | Function | Is an item of `Annotated` metadata a rule or a predicate.                |
| `key_candidates`      | Function | What a JSON key text might stand for (`"1"` → `1`, `"true"` → `True`).   |
| `name_json_type`      | Function | The JSON kind of a value in a few words, for cards.                      |
| `resolve_type_hints`  | Function | The real types of a class's fields, type variables filled in.            |
| `substitute_type_vars`| Function | Used by `resolve_type_hints`; not imported from outside this folder.     |
"""
