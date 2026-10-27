import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._helpers import closest_failure


def _failure(label):
    return DeserializationError(label=label)


def test_no_failures_give_none():
    assert closest_failure([]) is None
    assert closest_failure(()) is None


def test_one_failure_is_the_closest():
    only = _failure("$.pt")

    assert closest_failure([only]) is only


def test_the_deeper_failure_wins_even_when_it_is_second():
    shallow = _failure("$.pt")
    deep = _failure("$.pt.x")

    assert closest_failure([shallow, deep]) is deep


def test_the_deeper_failure_wins_even_when_it_is_first():
    deep = _failure("$.pt.x")
    shallow = _failure("$.pt")

    assert closest_failure([deep, shallow]) is deep


def test_a_tie_keeps_the_first():
    first = _failure("$.aa")
    second = _failure("$.bb")

    assert closest_failure([first, second]) is first


def test_a_failure_without_a_label_counts_as_the_shallowest():
    unlabeled = _failure(None)
    labeled = _failure("$")

    assert closest_failure([unlabeled, labeled]) is labeled


def test_failures_without_labels_keep_the_first():
    first, second = _failure(None), _failure(None)

    assert closest_failure([first, second]) is first


def test_an_error_that_has_no_label_attribute_at_all_does_not_break_it():
    plain = ValueError("no label here")
    labeled = _failure("$.x")

    assert closest_failure([plain, labeled]) is labeled
    assert closest_failure([plain]) is plain
