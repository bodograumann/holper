from datetime import date
from importlib.resources import files
from unittest import TestCase

from holper.iof import (
    ClassList,
    CompetitorList,
    CourseData,
    EntryList,
    EventList,
    OrganisationList,
    ResultList,
    StartList,
)

from . import IOFv3


class TestClassList(TestCase):
    def test_read_open_example(self):
        xml_data = (files(IOFv3) / "ClassList.xml").read_bytes()
        class_list = ClassList.from_xml(xml_data)

        assert len(class_list.classes) == 2
        assert class_list.classes[0].id.text == "1"
        assert len(class_list.classes[0].legs) == 3
        assert class_list.classes[1].id.text == "2"
        assert len(class_list.classes[1].legs) == 3

    def test_read_individual_example(self):
        xml_data = (files(IOFv3) / "ClassList_Individual_Step1.xml").read_bytes()
        class_list = ClassList.from_xml(xml_data)

        assert len(class_list.classes) == 2
        assert class_list.classes[0].number_of_competitors == 60
        assert class_list.classes[1].number_of_competitors == 60

    def test_read_relay_example(self):
        xml_data = (files(IOFv3) / "ClassList_Relay_Step1.xml").read_bytes()
        class_list = ClassList.from_xml(xml_data)

        assert len(class_list.classes) == 2
        assert class_list.classes[0].number_of_competitors == 35
        assert class_list.classes[1].number_of_competitors == 38


class TestCompetitorList(TestCase):
    def test_read_example(self):
        xml_data = (files(IOFv3) / "CompetitorList.xml").read_bytes()
        competitor_list = CompetitorList.from_xml(xml_data)

        assert len(competitor_list.competitors) == 4
        assert len(competitor_list.competitors[0].organisations) == 2


class TestCourseData(TestCase):
    def test_read_individual_example1(self):
        xml_data = (files(IOFv3) / "CourseData_Individual_Step2.xml").read_bytes()
        course_data = CourseData.from_xml(xml_data)

        assert course_data.iof_version == "3.0"
        assert course_data.event.name == "Example event"
        assert course_data.event.start_time.date == date.fromisoformat("2011-07-30")
        assert len(course_data.race_course_data) == 1
        race = course_data.race_course_data[0]
        assert len(race.controls) == 8
        assert len(race.courses) == 2
        assert len(race.courses[0].course_controls) == 10
        assert len(race.courses[1].course_controls) == 10
        assert len(race.class_course_assignments) == 2

    def test_read_individual_example2(self):
        xml_data = (files(IOFv3) / "CourseData_Individual_Step4.xml").read_bytes()
        course_data = CourseData.from_xml(xml_data)

        race = course_data.race_course_data[0]
        assert len(race.courses) == 2
        assert len(race.class_course_assignments) == 0
        assert len(race.person_course_assignments) == 2

    def test_read_relay_example1(self):
        xml_data = (files(IOFv3) / "CourseData_Relay_Step2.xml").read_bytes()
        course_data = CourseData.from_xml(xml_data)

        race = course_data.race_course_data[0]
        assert len(race.courses) == 3
        assert len(race.class_course_assignments) == 4
        assert len(race.class_course_assignments[0].allowed_on_legs) == 2
        assert len(race.class_course_assignments[1].allowed_on_legs) == 1
        assert len(race.class_course_assignments[2].allowed_on_legs) == 2
        assert len(race.class_course_assignments[3].allowed_on_legs) == 1

    def test_read_relay_example2(self):
        xml_data = (files(IOFv3) / "CourseData_Relay_Step4.xml").read_bytes()
        course_data = CourseData.from_xml(xml_data)

        race = course_data.race_course_data[0]
        assert len(race.courses) == 3
        assert len(race.team_course_assignments) == 2
        assert len(race.team_course_assignments[0].team_member_course_assignments) == 5
        assert len(race.team_course_assignments[1].team_member_course_assignments) == 5


class TestEntryList(TestCase):
    def test_read_example1(self):
        xml_data = (files(IOFv3) / "EntryList1.xml").read_bytes()
        entry_list = EntryList.from_xml(xml_data)

        assert entry_list.event.name == "Example event"
        assert len(entry_list.person_entries) == 3
        assert entry_list.person_entries[0].person.ids[0].text == "1"
        assert entry_list.person_entries[0].organisation.id.text == "5"

    def test_read_example2(self):
        xml_data = (files(IOFv3) / "EntryList2.xml").read_bytes()
        entry_list = EntryList.from_xml(xml_data)

        assert entry_list.event.name == "Example event"
        assert len(entry_list.team_entries) == 2
        assert len(entry_list.team_entries[0].team_entry_persons) == 5


class TestEventList(TestCase):
    def test_read_example(self):
        xml_data = (files(IOFv3) / "Event_name_and_start_time.xml").read_bytes()
        event_list = EventList.from_xml(xml_data)

        assert len(event_list.events) == 1


class TestOrganisationList(TestCase):
    def test_read_example(self):
        xml_data = (files(IOFv3) / "OrganisationList.xml").read_bytes()
        organisation_list = OrganisationList.from_xml(xml_data)

        assert len(organisation_list.organisations) == 4


class TestResultList(TestCase):
    def test_read_example1(self):
        xml_data = (files(IOFv3) / "ResultList1.xml").read_bytes()
        result_list = ResultList.from_xml(xml_data)

        assert len(result_list.class_results) == 2
        assert len(result_list.class_results[0].person_results) == 2
        assert len(result_list.class_results[0].person_results[0].results) == 1
        assert len(result_list.class_results[0].person_results[0].results[0].split_times) == 5

    def test_read_example2(self):
        xml_data = (files(IOFv3) / "ResultList2.xml").read_bytes()
        result_list = ResultList.from_xml(xml_data)

        assert len(result_list.class_results) == 1
        assert len(result_list.class_results[0].team_results) == 3
        assert len(result_list.class_results[0].team_results[0].team_member_results) == 5
        assert len(result_list.class_results[0].team_results[0].team_member_results[0].results) == 1
        assert len(result_list.class_results[0].team_results[0].team_member_results[0].results[0].split_times) == 3

    def test_read_example3(self):
        xml_data = (files(IOFv3) / "ResultList3.xml").read_bytes()
        result_list = ResultList.from_xml(xml_data)

        assert len(result_list.class_results) == 1
        assert len(result_list.class_results[0].courses) == 2
        assert len(result_list.class_results[0].person_results) == 2
        assert len(result_list.class_results[0].person_results[0].results) == 2
        assert result_list.class_results[0].person_results[0].results[0].race_number == 1
        assert len(result_list.class_results[0].person_results[0].results[0].split_times) == 5
        assert result_list.class_results[0].person_results[0].results[1].race_number == 2
        assert len(result_list.class_results[0].person_results[0].results[1].split_times) == 5

    def test_read_example4(self):
        xml_data = (files(IOFv3) / "ResultList4.xml").read_bytes()
        result_list = ResultList.from_xml(xml_data)

        assert len(result_list.class_results) == 1
        assert len(result_list.class_results[0].person_results) == 2
        assert len(result_list.class_results[0].person_results[0].results) == 1
        assert len(result_list.class_results[0].person_results[0].results[0].split_times) == 0
        # Note: We don't support the Extensions in this example. They are ignored.


class TestStartList(TestCase):
    def test_read_example1(self):
        xml_data = (files(IOFv3) / "StartList1.xml").read_bytes()
        start_list = StartList.from_xml(xml_data)

        assert len(start_list.class_starts) == 2
        assert len(start_list.class_starts[0].person_starts) == 2
        assert len(start_list.class_starts[0].person_starts[0].starts) == 1

    def test_read_example2(self):
        xml_data = (files(IOFv3) / "StartList2.xml").read_bytes()
        start_list = StartList.from_xml(xml_data)

        assert len(start_list.class_starts) == 1
        assert len(start_list.class_starts[0].team_starts) == 2
        assert len(start_list.class_starts[0].team_starts[0].team_member_starts) == 5
        assert len(start_list.class_starts[0].team_starts[0].team_member_starts[0].starts) == 1

    def test_read_example3(self):
        xml_data = (files(IOFv3) / "StartList3.xml").read_bytes()
        start_list = StartList.from_xml(xml_data)

        assert len(start_list.class_starts) == 1
        assert len(start_list.class_starts[0].person_starts) == 2
        assert len(start_list.class_starts[0].person_starts[0].starts) == 2

    def test_read_example4(self):
        xml_data = (files(IOFv3) / "StartList4.xml").read_bytes()
        start_list = StartList.from_xml(xml_data)

        assert len(start_list.class_starts) == 1
        assert len(start_list.class_starts[0].team_starts) == 2
        assert len(start_list.class_starts[0].team_starts[0].team_member_starts) == 5
        assert len(start_list.class_starts[0].team_starts[0].team_member_starts[0].starts) == 1

    def test_read_individual_example(self):
        xml_data = (files(IOFv3) / "StartList_Individual_Step3.xml").read_bytes()
        start_list = StartList.from_xml(xml_data)

        assert len(start_list.class_starts) == 1
        assert len(start_list.class_starts[0].person_starts) == 2
        assert len(start_list.class_starts[0].person_starts[0].starts) == 1

    def test_read_relay_example(self):
        xml_data = (files(IOFv3) / "StartList_Relay_Step3.xml").read_bytes()
        start_list = StartList.from_xml(xml_data)

        assert len(start_list.class_starts) == 1
        assert len(start_list.class_starts[0].team_starts) == 2
        assert len(start_list.class_starts[0].team_starts[0].team_member_starts) == 5
        assert len(start_list.class_starts[0].team_starts[0].team_member_starts[0].starts) == 1
