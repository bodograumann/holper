from pathlib import Path
from unittest import TestCase

import pytest

from holper import core, iofxml3, model


class TestModel(TestCase):
    session = None

    @classmethod
    def setUpClass(cls):
        cls.session = core.open_session("sqlite:///:memory:")

    def setUp(self):
        self.session.begin_nested()

    def tearDown(self):
        self.session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.session.rollback()

    def test_event(self):
        event1 = model.Event(event_id=1, name="event1", form=model.EventForm.RELAY)
        self.session.add(event1)

        event1a = self.session.merge(model.Event(event_id=1, name="event1a"))

        assert event1 is event1a


class TestImport(TestCase):
    def test_iofxml3_category_list(self):
        with Path("tests/IOFv3/ClassList_Individual_Step1.xml").open("rb") as file:
            categories = list(iofxml3.read(file))
            assert len(categories) == 2

    def test_iofxml3_person_entry_list(self):
        with Path("tests/IOFv3/EntryList1.xml").open("rb") as file:
            generator = iofxml3.read(file)
            _event = next(generator)
            entries = list(generator)
            assert len(entries) == 3

            for entry in entries:
                assert isinstance(entry, model.Entry)

            assert entries[0].category_requests[0].event_category is entries[1].category_requests[0].event_category
            assert entries[0].competitors[0].organisation.country.ioc_code == "GBR"

    def test_iofxml3_team_entry_list(self):
        with Path("tests/IOFv3/EntryList2.xml").open("rb") as file:
            generator = iofxml3.read(file)
            _event = next(generator)
            entries = list(generator)
            assert len(entries) == 2

            for entry in entries:
                assert isinstance(entry, model.Entry)

            assert len(entries[0].competitors) == 5

    def test_iofxml3_course_data(self):
        with Path("tests/IOFv3/CourseData_Individual_Step2.xml").open("rb") as file:
            generator = iofxml3.read(file)
            event = next(generator)
            race = next(generator)
            pytest.raises(StopIteration, lambda: next(generator))

            assert race.event == event
            assert len(race.courses) == 2
            assert len(race.categories) == 2
            assert race.categories[0].event_category == event.event_categories[0]
            assert race.categories[0].courses[0].course.name in [course.name for course in race.courses]
