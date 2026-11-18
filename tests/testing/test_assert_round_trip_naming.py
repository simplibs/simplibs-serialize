"""
Tests for assert_round_trip — the subtest names, `intro`, and `verbose=False`.
"""
from contextlib import contextmanager
from dataclasses import dataclass

import pytest

from simplibs.serialize.testing import assert_round_trip


@dataclass
class Point:
    x: int
    y: int


class RecordingSubtests:
    """Records the names of the subtests."""

    def __init__(self) -> None:
        self.names: list[str] = []

    @contextmanager
    def test(self, msg=None, **kwargs):
        self.names.append(msg)
        yield


def test_names_start_with_the_name_of_the_annotation():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Point(1, 2))

    assert all(name.startswith("[Point] ") for name in subtests.names)
    assert len(subtests.names) == 4


def test_two_calls_in_one_test_give_different_names():
    """Verify the reason for the prefix: with identical names a report could not say which value failed."""
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Point(1, 2))
    assert_round_trip(subtests, [Point(1, 2)], list[Point])

    assert len(subtests.names) == len(set(subtests.names)) == 8
    assert subtests.names[4].startswith("[list[")


def test_intro_replaces_the_annotation_prefix():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Point(1, 2), intro="case 1:")

    assert subtests.names[0] == "case 1: serialize returns valid JSON-compatible data"
    assert not any("[Point]" in name for name in subtests.names)


def test_verbose_false_needs_no_subtests_fixture():
    """Verify that with verbose=False no subtest is created, so `subtests` may be None."""
    assert_round_trip(None, Point(1, 2), verbose=False)


def test_verbose_false_raises_at_the_first_failed_check():
    with pytest.raises(Exception):
        assert_round_trip(None, object(), verbose=False)
