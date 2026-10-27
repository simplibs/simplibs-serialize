from dataclasses import dataclass
from typing import Annotated, Any, Generic, NamedTuple, NotRequired, Optional, TypedDict, TypeVar

import pytest

from simplibs.serialize.logic.deserializer._helpers import resolve_type_hints


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
Bounded = TypeVar("Bounded", bound=int)


@dataclass
class Plain:
    a: int
    b: str


@dataclass
class WithTextAnnotations:
    a: "int"
    b: "list[str]"


@dataclass
class WithForwardReference:
    child: "Later"


@dataclass
class Later:
    value: int


@dataclass
class WithAnnotated:
    a: Annotated[int, "doc"]


@dataclass
class Box(Generic[T]):
    item: T
    items: list[T]
    maybe: T | None
    plain: str


@dataclass
class Pair(Generic[K, V]):
    table: dict[K, V]


@dataclass
class BoundedBox(Generic[Bounded]):
    item: Bounded


@dataclass
class Unresolvable:
    a: "DoesNotExist"  # noqa: F821


class TypedPoint(NamedTuple):
    x: int
    y: str


class Options(TypedDict):
    name: str
    note: NotRequired[int]


def test_plain_dataclass():
    assert resolve_type_hints(Plain) == {"a": int, "b": str}


def test_named_tuple_and_typed_dict():
    assert resolve_type_hints(TypedPoint) == {"x": int, "y": str}
    assert resolve_type_hints(Options) == {"name": str, "note": NotRequired[int]}


def test_annotations_written_as_text_become_real_types():
    assert resolve_type_hints(WithTextAnnotations) == {"a": int, "b": list[str]}


def test_a_forward_reference_becomes_the_class():
    assert resolve_type_hints(WithForwardReference) == {"child": Later}


def test_annotated_is_kept_so_that_its_rules_still_run():
    assert resolve_type_hints(WithAnnotated) == {"a": Annotated[int, "doc"]}


def test_a_parameterized_generic_fills_in_its_type_variable():
    assert resolve_type_hints(Box[int]) == {
        "item": int,
        "items": list[int],
        "maybe": int | None,
        "plain": str,
    }


def test_a_generic_with_two_variables():
    assert resolve_type_hints(Pair[str, int]) == {"table": dict[str, int]}


def test_a_bare_generic_leaves_the_variable_to_any():
    assert resolve_type_hints(Box) == {
        "item": Any,
        "items": list[Any],
        "maybe": Optional[Any],
        "plain": str,
    }


def test_a_bare_generic_leaves_a_bound_variable_to_its_bound():
    assert resolve_type_hints(BoundedBox) == {"item": int}
    assert resolve_type_hints(BoundedBox[bool]) == {"item": bool}


def test_a_reference_that_cannot_be_resolved_raises():
    with pytest.raises(NameError):
        resolve_type_hints(Unresolvable)
