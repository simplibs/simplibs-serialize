from simplibs.serialize.logic.serializer._classes import SerializeContext


def _encode_value(obj, location, context):
    return ("encoded", obj, location, context)


def _context(**options) -> SerializeContext:
    return SerializeContext(default=None, allow_nan=False, encode_value=_encode_value, **options)


def test_stores_what_it_is_given():
    default = lambda obj: 0

    context = SerializeContext(default=default, allow_nan=True, encode_value=_encode_value)

    assert context.default is default
    assert context.allow_nan is True
    assert context.encode_value is _encode_value


def test_ancestors_start_empty():
    assert _context().ancestors == set()


def test_encode_delegates_to_encode_value_with_itself_as_the_context():
    context = _context()

    result = context.encode("value", ("items", 2))

    assert result == ("encoded", "value", ("items", 2), context)
    assert result[3] is context


def test_two_contexts_do_not_share_ancestors():
    first, second = _context(), _context()

    first.ancestors.add(1)

    assert second.ancestors == set()


def test_is_not_frozen():
    """`ancestors` changes during the walk, and a switch can be flipped."""
    context = _context()

    context.allow_nan = True
    context.ancestors.add(7)

    assert context.allow_nan is True
    assert context.ancestors == {7}
