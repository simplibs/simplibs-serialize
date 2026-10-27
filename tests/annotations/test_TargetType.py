from typing import Any

from simplibs.serialize.annotations import TargetType


def test_is_any():
    """Python has no type for 'any annotation', so the alias is `Any` with an honest name."""
    assert TargetType is Any
