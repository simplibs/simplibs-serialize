import dataclasses
from dataclasses import dataclass

import pytest

from simplibs.serialize import DeserializationError, deserialize, serialize, serialized_field
from simplibs.serialize.testing import assert_round_trip


_KEY = "simplibs.serialize"


def _only_field(**options) -> dataclasses.Field:
    """Build a real dataclass with one field made by serialized_field, and return that field."""

    @dataclass
    class Sample:
        value: int = serialized_field(**options)

    return dataclasses.fields(Sample)[0]


# ---------- the options written into the metadata ----------

def test_without_options_the_field_has_no_metadata():
    assert dict(_only_field().metadata) == {}


def test_alias_is_written_down():
    assert dict(_only_field(alias="userName").metadata) == {_KEY: {"alias": "userName"}}


def test_exclusion_is_written_down():
    assert dict(_only_field(exclude=True).metadata) == {_KEY: {"exclude": True}}


def test_exclusion_switched_off_writes_nothing():
    assert dict(_only_field(exclude=False).metadata) == {}


def test_both_options_are_written_down_together():
    metadata = dict(_only_field(alias="userName", exclude=True).metadata)

    assert metadata == {_KEY: {"alias": "userName", "exclude": True}}


# ---------- the caller's own metadata ----------

def test_callers_metadata_survives_next_to_the_options():
    metadata = dict(_only_field(alias="userName", metadata={"other": 1}).metadata)

    assert metadata == {"other": 1, _KEY: {"alias": "userName"}}


def test_callers_mapping_is_not_changed_and_not_linked():
    own = {"other": 1}

    field = _only_field(alias="userName", metadata=own)
    own["late"] = 2

    assert "late" not in field.metadata
    assert _KEY not in own


# ---------- everything else is dataclasses.field ----------

def test_default_reaches_the_field():
    assert _only_field(default=5).default == 5


def test_default_factory_reaches_the_field():
    assert _only_field(default_factory=list).default_factory is list


def test_init_false_reaches_the_field():
    assert _only_field(default=0, init=False).init is False


def test_kw_only_reaches_the_field():
    assert _only_field(kw_only=True).kw_only is True


def test_repr_compare_and_hash_reach_the_field():
    field = _only_field(repr=False, compare=False, hash=True)

    assert (field.repr, field.compare, field.hash) == (False, False, True)


def test_without_arguments_it_is_a_plain_required_field():
    field = _only_field()

    assert field.default is dataclasses.MISSING
    assert field.default_factory is dataclasses.MISSING
    assert (field.init, field.repr, field.compare, field.hash) == (True, True, True, None)


# ---------- with serialize and deserialize ----------

@dataclass
class User:
    user_name: str = serialized_field(alias="userName")
    cache: dict = serialized_field(exclude=True, default_factory=dict, compare=False)


@dataclass
class Unbuildable:
    secret: str = serialized_field(exclude=True)


def test_serialize_writes_the_alias_and_leaves_the_excluded_field_out():
    assert serialize(User("ann", cache={"k": 1})) == {"userName": "ann"}


def test_deserialize_reads_the_alias_and_leaves_the_excluded_field_to_its_default():
    user = deserialize({"userName": "ann"}, User)

    assert user == User("ann")
    assert user.cache == {}


def test_the_python_name_is_not_the_name_in_the_data():
    with pytest.raises(DeserializationError):
        deserialize({"user_name": "ann"}, User)


def test_an_excluded_field_without_a_default_cannot_be_built_back():
    assert serialize(Unbuildable("s")) == {}

    with pytest.raises(DeserializationError):
        deserialize({}, Unbuildable)


def test_round_trip_with_alias_and_exclusion(subtests):
    assert_round_trip(subtests, User("ann"))
