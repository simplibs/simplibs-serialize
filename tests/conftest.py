import pytest

from simplibs.serialize.logic.registry._handlers.active import FROM_HANDLERS, TO_HANDLERS


@pytest.fixture(autouse=True)
def restore_registry():
    """Put both live handler tables back as they were, whatever a test registered.

    The registry is global: a type registered in one test would otherwise be known
    to every test that runs after it.
    """
    to_before = dict(TO_HANDLERS)
    from_before = dict(FROM_HANDLERS)

    yield

    TO_HANDLERS.clear()
    TO_HANDLERS.update(to_before)
    FROM_HANDLERS.clear()
    FROM_HANDLERS.update(from_before)
