import dataclasses
from types import MappingProxyType

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import serialized_field
from simplibs.serialize.logic._common_helpers import get_field_options


_KEY = "simplibs.serialize"


def _field(metadata=None):
    """Build a real dataclass field named `value`, with the given metadata."""
    body = {"__annotations__": {"value": int}, "value": dataclasses.field(default=0, metadata=metadata or {})}
    return dataclasses.fields(dataclasses.dataclass(type("Sample", (), body)))[0]


@pytest.mark.parametrize(
    "options, expected",
    [
        pytest.param(None, ("value", False), id="no_options_at_all"),
        pytest.param({}, ("value", False), id="empty_options"),
        pytest.param({"alias": "userName"}, ("userName", False), id="alias_only"),
        pytest.param({"exclude": True}, ("value", True), id="exclusion_only"),
        pytest.param({"exclude": False}, ("value", False), id="exclusion_switched_off"),
        pytest.param({"alias": "userName", "exclude": True}, ("userName", True), id="both"),
        pytest.param({"alias": None}, ("value", False), id="alias_none"),
        pytest.param(MappingProxyType({"alias": "userName"}), ("userName", False), id="any_mapping"),
    ],
)
def test_reads_the_options(options, expected):
    metadata = None if options is None else {_KEY: options}

    assert get_field_options(_field(metadata)) == expected


def test_reads_what_serialized_field_wrote():
    @dataclasses.dataclass
    class Sample:
        user_name: str = serialized_field(alias="userName", exclude=True, default="")

    assert get_field_options(dataclasses.fields(Sample)[0]) == ("userName", True)


def test_other_metadata_is_not_ours():
    assert get_field_options(_field({"other_tool": {"alias": 5}})) == ("value", False)


@pytest.mark.parametrize(
    "options, problem",
    [
        pytest.param("yes", "The options are not a mapping.", id="not_a_mapping"),
        pytest.param({"alais": "x"}, "Unknown option(s): 'alais'.", id="unknown_option"),
        pytest.param({"b": 1, "a": 2}, "Unknown option(s): 'a', 'b'.", id="unknown_options_sorted"),
        pytest.param({"alias": ""}, "The alias is not a non-empty text.", id="empty_alias"),
        pytest.param({"alias": 5}, "The alias is not a non-empty text.", id="alias_not_text"),
        pytest.param({"exclude": "yes"}, "The exclusion is not a bool.", id="exclusion_text"),
        pytest.param({"exclude": 1}, "The exclusion is not a bool.", id="exclusion_int"),
    ],
)
def test_raises_param_error_for_broken_options(options, problem):
    with pytest.raises(ParamError) as caught:
        get_field_options(_field({_KEY: options}))

    exc = caught.value
    assert exc.error_name == "SERIALIZE_INVALID_FIELD_OPTIONS"
    assert exc.label == "field 'value' metadata"
    assert exc.value == options
    assert problem in str(exc.problem)
