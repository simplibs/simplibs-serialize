import dataclasses
from dataclasses import dataclass, field

import pytest

from simplibs.serialize.logic.deserializer._helpers import has_default


@dataclass
class Sample:
    required: int
    with_default: int = 5
    with_none: object = None
    with_factory: list = field(default_factory=list)
    with_zero_init: int = field(default=0, init=False)


def _field(name):
    return {f.name: f for f in dataclasses.fields(Sample)}[name]


def test_a_field_without_a_default_has_none():
    assert has_default(_field("required")) is False


@pytest.mark.parametrize(
    "name",
    ["with_default", "with_none", "with_factory", "with_zero_init"],
    ids=["plain_default", "default_none", "default_factory", "not_in_init"],
)
def test_a_field_with_any_kind_of_default_has_one(name):
    assert has_default(_field(name)) is True
