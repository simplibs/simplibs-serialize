from collections import OrderedDict, defaultdict, abc

import pytest

from simplibs.serialize.logic.deserializer._builders import BUILDER_TABLE, build_mapping_value
from simplibs.serialize.logic.deserializer._builders.constants import MAPPING_FACTORIES


def test_is_read_only():
    with pytest.raises(TypeError):
        MAPPING_FACTORIES[dict] = dict


def test_knows_exactly_one_origin():
    assert set(MAPPING_FACTORIES) == {OrderedDict}


def test_ordered_dict_keeps_the_order_of_the_built_dict():
    result = MAPPING_FACTORIES[OrderedDict]({"b": 1, "a": 2})

    assert type(result) is OrderedDict
    assert list(result) == ["b", "a"]


@pytest.mark.parametrize(
    "origin",
    [dict, abc.Mapping, abc.MutableMapping, defaultdict],
    ids=lambda origin: origin.__name__,
)
def test_everything_else_is_left_to_stay_a_dict(origin):
    assert origin not in MAPPING_FACTORIES


def test_every_origin_is_one_the_mapping_builder_serves():
    assert all(BUILDER_TABLE[origin] is build_mapping_value for origin in MAPPING_FACTORIES)
