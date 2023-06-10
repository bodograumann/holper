from datetime import datetime
from itertools import chain

from pydantic_xml import BaseXmlModel, attr, element, wrapped
# Unsupported:
# - forward refs with `from future import annotated`

nsmap = {
    "": "http://www.orienteering.org/datastandard/3.0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


class IOFBaseModel(BaseXmlModel, nsmap=nsmap, search_mode="ordered"):
    pass


class ClassCourseAssignment(IOFBaseModel):
    class_name: str = element(tag="ClassName")
    course_name: str = element(tag="CourseName")


class TeamMemberCourseAssignment(IOFBaseModel):
    leg: int = element(tag="Leg")
    course_name: str = element(tag="CourseName")
    course_family: str = element(tag="CourseFamily")


class TeamCourseAssignment(IOFBaseModel):
    bib_number: str = element(tag="BibNumber")
    team_member_course_assignments: list[TeamMemberCourseAssignment] = element(tag="TeamMemberCourseAssignment")


class CourseControl(IOFBaseModel):
    type: str = attr()
    control: str = element(tag="Control")
    leg_length: int | None = element(tag="LegLength")


class Course(IOFBaseModel):
    name: str = element(tag="Name")
    course_family: str | None = element(tag="CourseFamily")
    length: int = element(tag="Length")
    climb: int = element(tag="Climb")
    course_controls: list[CourseControl] | None = element(tag="CourseControl")


class MapPosition(IOFBaseModel):
    x: float = attr()
    y: float = attr()
    unit: str = attr()


class Control(IOFBaseModel):
    control_id: str = element(tag="Id")
    map_position: MapPosition = element(tag="MapPosition")


class Map(IOFBaseModel):
    scale: int = element(tag="Scale")


class RaceCourseData(IOFBaseModel):
    map: Map = element(tag="Map")
    controls: list[Control] = element(tag="Control")
    courses: list[Course] = element(tag="Course")
    team_course_assignments: list[TeamCourseAssignment] | None = element(tag="TeamCourseAssignment")
    class_course_assignments: list[ClassCourseAssignment] | None = element(tag="ClassCourseAssignment")

    def delete_unused_courses(self):
        used_courses = [
            assignment.course_name
            for assignment in chain(
                chain.from_iterable(
                    team_assignment.team_member_course_assignments for team_assignment in self.team_course_assignments
                ),
                self.class_course_assignments,
            )
        ]
        self.courses = [course for course in self.courses if course.name in used_courses]


class Event(IOFBaseModel):
    name: str = element(tag="Name")


class CourseData(IOFBaseModel):
    iof_version: str = attr(name="iofVersion")
    create_time: datetime = attr(name="createTime")
    creator: str = attr()

    event: Event = element(tag="Event")
    race_course_data: RaceCourseData = element(tag="RaceCourseData")
