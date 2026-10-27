import dataclasses


def has_default(
    field: dataclasses.Field
) -> bool:
    """Return True if a dataclass field can be left out of the constructor call.

    Args:
        field: A field from `dataclasses.fields(...)`.
    """

    # 1. A plain default or a factory
    return (
        field.default is not dataclasses.MISSING
        or field.default_factory is not dataclasses.MISSING
    )


_DESIGN_NOTES = """
# has_default — May This Field Be Missing

## Purpose
Missing data is fine for a field the class can fill itself, and an error for
one it cannot.
"""
