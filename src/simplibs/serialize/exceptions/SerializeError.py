from simplibs.exception import ConversionError


class SerializeError(ConversionError):
    """Root exception class for all errors originating from simplibs-serialize."""


_DESIGN_NOTES = """
# SerializeError — One Root for the Whole Library

## Purpose
`except SerializeError` catches everything this library raises, in either
direction.
"""
