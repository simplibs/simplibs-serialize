import dataclasses
from collections.abc import Mapping
# Outers
from .._constants import FIELD_ALIAS_OPTION, FIELD_EXCLUDE_OPTION, FIELD_METADATA_KEY
# Inners
from ._validations import raise_invalid_field_options_error


def get_field_options(
    field: dataclasses.Field
) -> tuple[str, bool]:
    """Read the serialize options of a dataclass field.

    Args:
        field: A field from `dataclasses.fields(...)`.

    Returns:
        The name of the field in the data (its alias, or its own name) and
        whether the field is excluded.

    Raises:
        ParamError: If the options under `FIELD_METADATA_KEY` are not valid.
    """

    # 1. A field without options is the common case
    options = field.metadata.get(FIELD_METADATA_KEY)
    if options is None:
        return field.name, False

    # 2. The options must be a mapping with known keys only — a typo
    #    such as "alais" would otherwise be ignored without a trace
    if not isinstance(options, Mapping):
        raise_invalid_field_options_error(field.name, options, "The options are not a mapping.")
    unknown = set(options) - {FIELD_ALIAS_OPTION, FIELD_EXCLUDE_OPTION}
    if unknown:
        raise_invalid_field_options_error(
            field.name, options, f"Unknown option(s): {', '.join(sorted(map(repr, unknown)))}.",
        )

    # 3. The alias is a non-empty text, or absent
    alias = options.get(FIELD_ALIAS_OPTION)
    if alias is not None and (not isinstance(alias, str) or not alias):
        raise_invalid_field_options_error(field.name, options, "The alias is not a non-empty text.")

    # 4. The exclusion is a bool, or absent
    exclude = options.get(FIELD_EXCLUDE_OPTION, False)
    if not isinstance(exclude, bool):
        raise_invalid_field_options_error(field.name, options, "The exclusion is not a bool.")

    # 5. The name in the data and the flag
    return (alias if alias is not None else field.name), exclude


_DESIGN_NOTES = """
# get_field_options — What a Field Says About Itself

## Purpose
The single reader of the options that `serialized_field` writes, so `serialize`
and `deserialize` cannot disagree about what a field is called in the data.

## Strict on Purpose
Unknown option names are an error. `serialized_field` cannot produce them; a
hand-written `metadata={"simplibs.serialize": {"alais": "x"}}` can, and a
silently ignored alias is a bug that shows up as data in the wrong place.

## `ParamError`
The mistake is in the class definition, not in the data being converted.
"""
