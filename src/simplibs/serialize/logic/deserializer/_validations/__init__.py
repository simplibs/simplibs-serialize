from .raise_build_failed_error import raise_build_failed_error
from .raise_data_too_deep_error import raise_data_too_deep_error
from .raise_invalid_key_error import raise_invalid_key_error
from .raise_key_collision_error import raise_key_collision_error
from .raise_literal_mismatch_error import raise_literal_mismatch_error
from .raise_missing_field_error import raise_missing_field_error
from .raise_rule_failed_error import raise_rule_failed_error
from .raise_union_ambiguous_error import raise_union_ambiguous_error
from .raise_union_no_match_error import raise_union_no_match_error
from .raise_unknown_field_error import raise_unknown_field_error
from .raise_unsupported_annotation_error import raise_unsupported_annotation_error
from .raise_wrong_length_error import raise_wrong_length_error
from .raise_wrong_type_error import raise_wrong_type_error


_DESIGN_NOTES = """
# Deserializer Validations Sub-Package

## Purpose
Diagnostic raisers for everything that can go wrong on the way back. Each `raise_*`
raises one `DeserializationError` card: `error_name`, `label` (the location of the
value), `value`, `problem`, `expected`, `how_to_fix`, `exception`.

## Internal Components Registry

| Component                            | Type     | Description                                               |
| :----------------------------------- | :------- | :-------------------------------------------------------- |
| `raise_unsupported_annotation_error` | Function | Nothing can build this annotation.                        |
| `raise_wrong_type_error`             | Function | The data is another kind than the annotation needs.       |
| `raise_wrong_length_error`           | Function | A tuple or `NamedTuple` of the wrong length.              |
| `raise_missing_field_error`          | Function | A required field or key is absent.                        |
| `raise_unknown_field_error`          | Function | A key the class does not have (strict).                   |
| `raise_key_collision_error`          | Function | Two keys of the data became one key of the mapping.       |
| `raise_build_failed_error`           | Function | A handler or a constructor raised.                        |
| `raise_union_no_match_error`         | Function | No member of a union fits.                                |
| `raise_union_ambiguous_error`        | Function | More than one member fits, none exactly.                  |
| `raise_rule_failed_error`            | Function | A rule of `Annotated` is not satisfied.                   |
| `raise_literal_mismatch_error`       | Function | Not one of the values of a `Literal`.                     |
| `raise_invalid_key_error`            | Function | A key text that is not a valid key of the annotated type. |
| `raise_data_too_deep_error`          | Function | Data nested beyond the interpreter's limit.               |

## Which Error Class
Everything that is wrong with the data is a `DeserializationError`. The one mistake in
the code (a dataclass field's `metadata`) is a `ParamError` from `logic/_helpers`.
"""
