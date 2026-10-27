from simplibs.serialize.logic.deserializer._classes import DeserializeContext


def _build_value(data, annotation, location, context):
    return ("built", data, annotation, location, context)


def test_stores_what_it_is_given():
    context = DeserializeContext(strict=False, build_value=_build_value)

    assert context.strict is False
    assert context.build_value is _build_value


def test_build_delegates_to_build_value_with_itself_as_the_context():
    context = DeserializeContext(strict=True, build_value=_build_value)

    result = context.build({"a": 1}, int, ("items", 2))

    assert result == ("built", {"a": 1}, int, ("items", 2), context)
    assert result[4] is context


def test_two_contexts_are_independent():
    strict = DeserializeContext(strict=True, build_value=_build_value)
    loose = DeserializeContext(strict=False, build_value=_build_value)

    assert strict.strict is True
    assert loose.strict is False
