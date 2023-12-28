import pytest

from holper import core, model


class TestModel:
    @pytest.fixture(scope="class")
    def session(self):
        return core.open_session("sqlite:///:memory:")

    @pytest.fixture(autouse=True)
    def _transaction(self, session):
        session.begin_nested()
        try:
            yield
        finally:
            session.rollback()

    def test_event(self, session):
        event1 = model.Event(event_id=1, name="event1", form=model.EventForm.RELAY)
        session.add(event1)

        event1a = session.merge(model.Event(event_id=1, name="event1a"))

        assert event1 is event1a
